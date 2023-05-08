import json
import re

import httpx
from app import pydantic_models as pm
from app import settings
from app.uzt_client import UZTClient

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def get_categories_from_page(client: UZTClient) -> pm.FResp:
    categories = list()
    a_list = client.tree.css("#ctl00_MainArea_UpdatePanel1 li a")
    for a in a_list:
        name = re.search(r"(.+) \(.+\)$", a.text()).group(1)
        href = a.attrs.get("href")
        category = pm.CategoryOut(name=name, href=href)
        categories.append(category.dict())
    if not categories:
        return pm.FResp(data="There are no categories on the page")
    return pm.FResp(status_ok=True, data=categories)


def send_data_to_api(endpoint: str, data: list[dict]):
    url = f"{settings.API_BASE_URL}{endpoint}"
    resp = httpx.post(url=url, headers=HEADERS, content=json.dumps(data))
    if resp.status_code != 201:
        return pm.FResp(data=resp)
    return pm.FResp(status_ok=True, data=resp)


def get_categories_from_api() -> pm.FResp:
    url = f"{settings.API_BASE_URL}/api/categories"
    try:
        resp = httpx.get(url=url, headers=HEADERS)
        data = [pm.CategoryIn(**item) for item in resp.json()]
        if not data:
            return pm.FResp(data="No data")
        return pm.FResp(status_ok=True, data=data)
    except Exception as e:
        return pm.FResp(data=e)


def find_and_send_categories_to_api():
    with UZTClient() as uzt:
        url = f"{settings.BASE_URL}{settings.START_URL}"
        uzt.get(url=url)
        categories_on_page = get_categories_from_page(uzt)
        if not categories_on_page:
            return pm.FResp(data="No categories found on the page")
        resp = send_data_to_api(
            endpoint="/api/categories/create", data=categories_on_page.data
        )
        return resp


def get_next_page_href(client: UZTClient):
    a = client.tree.css_first("table.Pager td:last-child a")
    if not a:
        return pm.FResp(data="There is not next page href")
    return pm.FResp(status_ok=True, data=a.attrs.get("href"))


def main():
    # Checking for the presence of categories in the API service.
    can_try = 3
    categories = None
    while can_try:
        check = get_categories_from_api()
        if check:
            categories = check.data
            break
        else:
            resp = find_and_send_categories_to_api()
            can_try -= 1
            if not can_try:
                raise Exception("Some error where trying get categories")

    print(categories)


if __name__ == "__main__":
    main()
