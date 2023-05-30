import json
import sys
from datetime import datetime, timedelta

import betterlogging as logging
import httpx

from sendler.app.pydantic_models import Category, Job, Subscriber
from sendler.app.settings import settings

# import logging
logger = logging.getLogger('sendler')
logging.basic_colorized_config(level=logging.INFO)


def get_data_from_api(endpoint, data_class):
    data = list()
    resp = httpx.get(url=endpoint, headers=settings.api.headers)
    if resp.status_code != 200:
        resp.raise_for_status()
    for item in resp.json():
        data.append(data_class(**item))
    return data


def get_subscribers() -> list[Subscriber]:
    subscribers = get_data_from_api(settings.api.subscribers.get, Subscriber)
    return subscribers


def get_categories() -> list[Category]:
    categories = get_data_from_api(settings.api.categories.get, Category)
    return categories


def get_jobs(categories: list[Category]) -> list[list[Job]]:
    jobs_by_cat = []
    for category in categories:
        jobs = []
        jobs = get_data_from_api(
            settings.api.jobs.get.format(category.id), Job
        )
        jobs_by_cat.append(jobs)
    return jobs_by_cat


def get_subscriptions(subscriber):
    ...
    return


def get_state():
    state = dict()
    path = 'sendler/app/state.json'
    try:
        with open(path, 'r') as file:
            state = json.load(file)
    except FileNotFoundError:
        logger.error(f'File {path} not found')
    except json.decoder.JSONDecodeError:
        logger.info('File state.json is empty')
    return state


def main():
    try:
        subscribers = get_subscribers()
        categories = get_categories()
        jobs_by_cat = get_jobs(categories)

    except httpx.HTTPStatusError as e:
        logger.error(e)
        sys.exit(1)

    state = get_state()
    yesterday = datetime.today() - timedelta(days=1)

    last_succesful_mailing = state.get('last_succesful_mailing', yesterday)

    print(last_succesful_mailing)

    print(
        f'Total subscribers {len(subscribers)}, categories {len(categories)}, jobs {sum(len(jobs) for jobs in jobs_by_cat)}'
    )


if __name__ == '__main__':
    main()
