import argparse
import json
import re

import httpx
from app import pydantic_models as pd
from app import settings
from app.uzt_client import UZTClient
from loggers.loggers import log_info

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def get_categories_from_page(client: UZTClient) -> pd.FResp:
    categories = list()
    a_list = client.tree.css("#ctl00_MainArea_UpdatePanel1 li a")
    for a in a_list:
        name = re.search(r"(.+) \(.+\)$", a.text()).group(1)
        href = a.attrs.get("href")
        category = pd.CategoryOut(name=name, href=href)
        categories.append(category.dict())
    if not categories:
        return pd.FResp(data="There are no categories on the page")
    return pd.FResp(ok=True, data=categories)


def send_data_to_api(endpoint: str, data: list[dict] | dict):
    url = f"{settings.API_BASE_URL}{endpoint}"
    resp = httpx.post(url=url, headers=HEADERS, content=json.dumps(data))
    if resp.status_code != 201:
        return pd.FResp(data=resp)
    return pd.FResp(ok=True, data=resp)


def get_categories_from_api() -> pd.FResp:
    url = f"{settings.API_BASE_URL}/api/categories"
    try:
        resp = httpx.get(url=url, headers=HEADERS)
        data = [pd.CategoryIn(**item) for item in resp.json()]
        if not data:
            return pd.FResp(data="No data")
        return pd.FResp(ok=True, data=data)
    except Exception as e:
        return pd.FResp(data=e)


def find_and_send_categories_to_api():
    with UZTClient() as uzt:
        url = f"{settings.BASE_URL}{settings.START_URL}"
        uzt.get(url=url)
        categories_on_page = get_categories_from_page(uzt)
        if not categories_on_page:
            return pd.FResp(data="No categories found on the page")
        resp = send_data_to_api(
            endpoint="/api/categories/create", data=categories_on_page.data
        )
        return resp


def get_next_page_href(client: UZTClient):
    a = client.tree.css_first("table.Pager td:last-child a")
    if not a:
        return pd.FResp(data="There is not next page href")
    return pd.FResp(ok=True, data=a.attrs.get("href"))


def get_categories() -> list[pd.CategoryIn]:
    # Checking for the presence of categories in the API service.
    can_try = 3
    categories = None
    while can_try:
        check = get_categories_from_api()
        if check:
            categories = check.data
            break
        else:
            with UZTClient() as uzt:
                url = f"{settings.BASE_URL}{settings.START_URL}"
                uzt.get(url=url)
                categories_on_page = get_categories_from_page(uzt)
                send_data_to_api(
                    endpoint="/api/categories/create", data=categories_on_page.data
                )
            can_try -= 1
            if not can_try:
                raise Exception(
                    "Failed to retrieve categories neither from the database nor from the page"
                )

    return get_categories_slice(categories)


def get_categories_slice(categories):
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, help="From category id...")
    parser.add_argument("--end", type=int, help="To category id (iclusive)")

    args = parser.parse_args()
    start = args.start
    end = args.end

    if start and end:
        categories = list(
            filter(lambda item: item.id >= start and item.id <= end, categories)
        )
    elif start:
        categories = list(filter(lambda item: item.id >= start, categories))

    assert categories
    return categories


def get_jobs(category: pd.CategoryIn):
    jobs_list = list()
    with UZTClient() as uzt:
        url = f"{settings.BASE_URL}{settings.START_URL}"
        uzt.get(url=url)
        uzt.submit_asp_form(category.href)
        uzt.get(uzt.next_url)

        # -------------- log
        log_info(f'{category.id}: "{category.name}" is in working')

        while True:
            table = uzt.tree.css_first(
                "#ctl00_MainArea_SearchResultsList_POGrid")
            tr_list = table.css("tr:not(:nth-child(-n+2)):not(:last-child)")
            for tr in tr_list:
                cells = tr.css("td")
                date_from, date_to, title, company, place = [
                    item.text().strip() for item in tr.css("td")
                ]

                href = cells[2].css_first("a").attrs.get("href")
                uzt.submit_asp_form(href, only_url=True)

                long_url = uzt.next_url
                match = re.search(r"(^.+aspx\?).+(itemID.+)$", long_url)
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

            next_page = get_next_page_href(uzt)
            if not next_page:
                break
            uzt.submit_asp_form(next_page.data)

    return pd.FResp(ok=True, data=jobs_list)


def main():
    try:
        categories = get_categories()
    except httpx.ConnectError:
        log_info("No API cconnection.")
        exit()
    try:
        for category in categories:
            jobs_list: pd.FResp = get_jobs(category)
            if jobs_list:
                log_info(
                    f'{category.id}: "{category.name}" has {len(jobs_list.data)} jobs.'
                )

                resp = send_data_to_api(
                    f"/api/category/{category.id}/jobs/create", jobs_list.data
                )

                if resp and resp.data.status_code == 201:
                    created_jobs = resp.data.json()
                    total = len(created_jobs)
                    log_info(f"{total} new jobs were saved")

                else:
                    log_info("No new data was saved")
    except (UZTClient.AspInputsError, httpx.ConnectError) as e:
        log_info(f"ERROR --- {e}")
    log_info(
        "Mission accomplished! Now I can have some fun, or rather, I'm going to sleep..."
    )


if __name__ == "__main__":
    main()
