import asyncio

import httpx
from app.watcher import watcher

# ENDPOINT = "http://localhost:8000/api/category/{}/jobs"
ENDPOINT = "https://portal.uzt.lt/LDBPortal/Pages/PositionOpeningPublic/QuickPOSearch.aspx?no={}?branch=POSearch&pageId=aeff66fd-2d12-4e83-ae98-e0544bd1335c"


R = 3


async def perform_async_request(client, url):
    response = await client.get(url)
    return (url, response.status_code)


async def async_main(urls):
    async with httpx.AsyncClient() as client:
        tasks = list()
        for _ in range(R):
            for url in urls:
                tasks.append(perform_async_request(client, url))
        resp_list = await asyncio.gather(*tasks)
        print(resp_list)


def main(urls):
    asyncio.run(async_main(urls))


def main2(urls):
    resp_list = list()
    with httpx.Client() as client:
        for _ in range(R):
            for url in urls:
                response = client.get(url)
                resp_list.append((url, response.status_code))
    print(resp_list)


if __name__ == "__main__":
    urls = [ENDPOINT.format(category) for category in range(1, 20)]

    main(urls)
    print("\n\n")

    main2(urls)
