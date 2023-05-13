import asyncio
import timeit
from multiprocessing import Pool

import httpx


class AttrFromDict:
    def __init__(self, dictionary: dict):
        [setattr(self, key, value) for key, value in dictionary.items()]


async def log_request(request: httpx.Request):
    print(f"{request.method}: {request.url}")


async def log_response(response: httpx.Response):
    print(f"{response.request.url} status is: {response.status_code}")


async def get_product(url):
    async with httpx.AsyncClient(
        event_hooks={"response": [log_response], "request": [log_request]},
        verify=False,
        timeout=180,
    ) as client:
        resp = await client.get(url)
        result_list.append(resp.status_code)


async def main():
    url = "https://portal.uzt.lt/LDBPortal/Pages/PositionOpeningPublic/QuickPOSearch.aspx?no={}?branch=POSearch&pageId=aeff66fd-2d12-4e83-ae98-e0544bd1335c"
    urls = [url.format(i) for i in range(20)]
    tasks = [get_product(url) for url in urls]
    await asyncio.gather(*tasks)


def get_url(url):
    r = httpx.get(url, verify=False)
    print(r.request.url, r.status_code)
    return r


def main2():
    url = "https://portal.uzt.lt/LDBPortal/Pages/PositionOpeningPublic/QuickPOSearch.aspx?no={}&branch=POSearch&pageId=aeff66fd-2d12-4e83-ae98-e0544bd1335c"
    urls = [url.format(i) for i in range(20)]
    result_list.extend([get_url(url) for url in urls])


def asymain():
    asyncio.run(main())


if __name__ == "__main__":
    result_list = []
    # print(f"{timeit.timeit(asymain, number=1):.10f}")
    print(f"{timeit.timeit(main2, number=1):.10f}")

    print(len(result_list))

    # async
    # 18.3576432890
    # 500

    # sync
    # 179.3309867360
    # 500
