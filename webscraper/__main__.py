import argparse
import json
import logging
import logging.config
import re
import sys
from urllib.parse import urljoin

import httpx
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from webscraper.app import custom_exception as ce
from webscraper.app import pydantic_models as pd
from webscraper.app.settings import settings
from webscraper.app.uzt_client import UZTClient
from webscraper.loggers.settings import settings as logger_settings

logger = logging.getLogger(__name__)
logging.config.dictConfig(logger_settings)


def log_error_and_exit(error):
    logger.error(error)
    sys.exit()


def get_categories_from_page(client: UZTClient) -> list[dict]:
    categories = list()
    a_list = client.tree.css('#ctl00_MainArea_UpdatePanel1 li a')
    for a in a_list:
        name = re.search(r'(.+) \(.+\)$', a.text()).group(1)
        href = a.attrs.get('href')
        category = pd.CategoryOut(name=name, href=href)
        categories.append(category.dict())
    if not categories:
        raise ce.ScrappingError('There are no categories on the page')
    return categories


def save_data_to_api(url: str, data: list[dict] | dict) -> dict:
    resp = httpx.post(
        url=url, headers=settings.api.headers, content=json.dumps(data)
    )
    if resp.status_code != 201:
        resp.raise_for_status()
    return resp.json()


def get_categories_from_api() -> list[pd.CategoryIn]:
    url = settings.api.categories.get
    resp = httpx.get(url=url, headers=settings.api.headers)
    if not resp.status_code == 200:
        resp.raise_for_status()

    categories = [pd.CategoryIn(**item) for item in resp.json()]
    return categories


def find_and_send_categories_to_api():
    with UZTClient() as uzt:
        url = urljoin(settings.target.base_url, settings.target.start_url)
        uzt.get(url=url)
        categories_on_page = get_categories_from_page(uzt)
        resp = save_data_to_api(
            url=settings.api.categories.create, data=categories_on_page
        )
        return resp


def get_next_page_href(client: UZTClient):
    a = client.tree.css_first('table.Pager td:last-child a')
    if a:
        return a.attrs.get('href')


def get_categories() -> list[pd.CategoryIn]:
    # Checking for the presence of categories in the API service.
    can_try = 3
    categories = None
    while can_try:

        try:
            categories = get_categories_from_api()
        except httpx.HTTPStatusError as e:
            logger.error(e)
        else:
            break

        try:
            categories = find_and_send_categories_to_api()
        except httpx.ConnectTimeout as e:
            logger.error(e)
            can_try -= 1

        if not can_try:
            raise httpx.ConnectTimeout(
                'Failed to retrieve categories neither from the database nor from the page'
            )

    return categories


def get_categories_slice(categories):
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, help='From category id...')
    parser.add_argument('--end', type=int, help='To category id (iclusive)')
    parser.add_argument('--marker', type=str, help='Marker for log')

    args = parser.parse_args()
    start = args.start
    end = args.end

    if start and end:
        categories = list(
            filter(
                lambda item: item.id >= start and item.id <= end, categories
            )
        )
    elif start:
        categories = list(filter(lambda item: item.id >= start, categories))

    assert categories
    return categories


def get_jobs_total_count(uzt):
    total_jobs = 0
    try:
        total_jobs_text = uzt.tree.css_first(
            'tr#ctl00_MainArea_SearchResultsList_POGrid_ctl01.TopGridPager td table tbody tr td table tbody tr td span.GridView-RowCountText'
        ).text()
        if total_jobs_text:
            total_jobs = int(total_jobs_text.split(':')[-1])
    except:
        ...

    return total_jobs


def get_jobs(category: pd.CategoryIn):
    jobs_list = list()
    with UZTClient() as uzt:
        url = urljoin(settings.target.base_url, settings.target.start_url)
        uzt.get(url=url)
        uzt.submit_asp_form(category.href)
        uzt.get(uzt.next_url)

        # -------------- log

        total_jobs = get_jobs_total_count(uzt)
        logger.info(
            f'{category.id}: "{category.name}" total jobs: {total_jobs}'
        )
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            transient=True,
            auto_refresh=False,
        ) as progress:

            task = progress.add_task(
                f'Geting jobs in {category.name}', total=total_jobs
            )

            while not progress.finished:
                table = uzt.tree.css_first(
                    '#ctl00_MainArea_SearchResultsList_POGrid'
                )
                tr_list = table.css(
                    'tr:not(:nth-child(-n+2)):not(:last-child)'
                )
                for tr in tr_list:
                    cells = tr.css('td')
                    date_from, date_to, title, company, place = [
                        item.text().strip() for item in tr.css('td')
                    ]

                    href = cells[2].css_first('a').attrs.get('href')
                    uzt.submit_asp_form(href, only_url=True)

                    long_url = uzt.next_url
                    try:
                        match = re.search(
                            r'(^.+aspx\?).+(itemID.+)$', long_url
                        )
                        short_url = match.group(1) + match.group(2)

                        job = pd.Job(
                            date_from=date_from,
                            date_to=date_to,
                            title=title,
                            company=company,
                            place=place,
                            url=short_url,
                        )

                        jobs_list.append(job.dict())
                        progress.update(task, advance=1)
                        progress.refresh()
                    except TypeError as e:
                        logger.error(e)
                next_page = get_next_page_href(uzt)
                if not next_page:
                    progress.update(task, completed=total_jobs)
                    break
                uzt.submit_asp_form(next_page)

    return pd.FResp(ok=True, data=jobs_list)


def main():
    try:
        categories = get_categories()
        for category in categories:
            try:
                jobs_list = get_jobs(category)
                if jobs_list:

                    created_jobs = save_data_to_api(
                        url=settings.api.jobs.create.format(category.id),
                        data=jobs_list.data,
                    )
                    print(created_jobs)
                    total = len(created_jobs)
                    logger.info(f'{total} new jobs were saved')
            except (
                UZTClient.AspInputsError,
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.HTTPStatusError,
            ) as e:
                logger.info('No new jobs was saved')
                if hasattr(e, 'response') and e.response.status_code != 409:
                    logger.error(e)
        logger.info(
            "Mission accomplished! Now I can have some fun, or rather, I'm going to sleep..."
        )
    except (httpx.ConnectError, httpx.HTTPStatusError) as e:
        log_error_and_exit(e)


if __name__ == '__main__':
    main()
