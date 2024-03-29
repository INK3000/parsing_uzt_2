import argparse
import json
import logging
import logging.config
import re
import sys
from urllib.parse import urljoin

import httpx
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from .app import custom_exception as ce
from .app import pydantic_models as pd
from .app.settings import settings
from .app.uzt_client import UZTClient
from .loggers.settings import settings as logger_settings

logger = logging.getLogger(__name__)
logging.config.dictConfig(logger_settings)


def log_error_and_exit(error):
    logger.error(error)
    sys.exit(1)


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
    """
    if script run with args
    start and end are category.id

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, help='From category id...')
    parser.add_argument('--end', type=int, help='To category id (iclusive)')

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
    """
    returns jobs values from table's header
    """
    total_jobs = 0
    try:
        total_jobs_text = uzt.tree.css_first(
            'tr.TopGridPager td table tbody tr td table tbody tr td span.GridView-RowCountText'
        ).text()
        if total_jobs_text:
            total_jobs = int(total_jobs_text.split(':')[-1])
    except Exception as e:
        logger.error(e)

    return total_jobs


def get_jobs(category: pd.CategoryIn) -> list[dict]:
    """
    return list of jobs

    """

    jobs_list = list()
    with UZTClient() as uzt:
        # open start url and go to te category page
        url = urljoin(settings.target.base_url, settings.target.start_url)
        uzt.get(url=url)
        uzt.submit_asp_form(category.href)
        uzt.get(uzt.next_url)

        # get amounts of jobs on all pages from data in the header of table
        total_jobs = get_jobs_total_count(uzt)
        logger.info(
            f'{category.id}: "{category.name}" total jobs: {total_jobs}'
        )
        # create object for progress bar
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

            # start cycle for all pages in the categoty
            while True:

                # find all row tables, exclude first two (name of columns and e.t.c.)
                table = uzt.tree.css_first(
                    '#ctl00_MainArea_SearchResultsList_POGrid'
                )
                tr_list = table.css(
                    'tr:not(:nth-child(-n+2)):not(:last-child)'
                )
                # get all data in cell for all rows
                for tr in tr_list:
                    cells = tr.css('td')
                    date_from, date_to, title, company, place = [
                        item.text().strip() for item in tr.css('td')
                    ]

                    href = cells[2].css_first('a').attrs.get('href')

                    # Obtain the static URL via event target
                    # without navigating to the page;
                    # only_url=True allows the client remains on the category page.

                    uzt.submit_asp_form(href, only_url=True)

                    # get static url for job and short it
                    # don't create job oject if there is no static url
                    long_url = uzt.next_url
                    try:
                        re_match = re.search(
                            r'(^.+aspx\?).+(itemID.+)$', long_url
                        )
                        short_url = re_match.group(1) + re_match.group(2)

                        job = pd.Job(
                            date_from=date_from,
                            date_to=date_to,
                            title=title,
                            company=company,
                            place=place,
                            url=short_url,
                        )

                        jobs_list.append(job.dict())
                    except TypeError as e:
                        logger.error(e)

                    finally:
                        # update progress bar
                        progress.update(task, advance=1)
                        progress.refresh()

                next_page = get_next_page_href(uzt)
                if not next_page:
                    # if no more pages, progress bar should be completed
                    progress.update(task, completed=total_jobs)
                    break

                # else go to the next page
                uzt.submit_asp_form(next_page)

    return jobs_list


def main():
    logger.info('Starting scraper...')
    try:
        categories = get_categories()
        logger.info(f'Total categories: {len(categories)}')
        for category in categories:
            try:
                jobs_list = get_jobs(category)
                if jobs_list:

                    created_jobs = save_data_to_api(
                        url=settings.api.jobs.create.format(category.id),
                        data=jobs_list,
                    )
                    total = len(created_jobs)
                    logger.info(f'{total} new jobs were saved')
            except (
                UZTClient.AspInputsError,
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.HTTPStatusError,
                httpx.RemoteProtocolError,
            ) as e:
                logger.info('No new jobs were saved')
                # don't show httpx.HTTPStatusError if status_code is 409
                if not hasattr(e, 'response') or e.response.status_code != 409:
                    logger.error(e)

        logger.info(
            "Mission accomplished! Now I can have some fun, or rather, I'm going to sleep..."
        )
    except (httpx.ConnectError, httpx.HTTPStatusError) as e:
        log_error_and_exit(e)
    except KeyboardInterrupt:
        log_error_and_exit('Interrupted by user')


if __name__ == '__main__':
    main()
