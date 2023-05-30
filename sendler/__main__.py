import json
import sys
from datetime import datetime, timedelta

import betterlogging as logging
import httpx
import pytz

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


def get_jobs(categories: list[Category], date) -> dict[int, list[Job]]:
    jobs_by_cat = dict()
    for category in categories:
        jobs = []
        jobs = get_data_from_api(
            settings.api.jobs.get.format(category.id), Job
        )
        filtered_jobs = list(filter(lambda i: i.date_scraped >= date, jobs))
        if filtered_jobs:
            jobs_by_cat[category.id] = filtered_jobs
    return jobs_by_cat


def get_subscriptions(subscriber):
    ...
    return


def get_state(path):
    state = dict()
    try:
        with open(path, 'r') as file:
            state = json.load(file)
    except FileNotFoundError:
        logger.error(f'File {path} not found')
    except json.decoder.JSONDecodeError:
        logger.info('File state.json is empty')
    return state


def save_state(path, data):
    try:
        with open(path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        logger.error(e)


def get_last_successful_mailing(path):

    yesterday = datetime.now(pytz.utc) - timedelta(days=1)

    state = get_state(path)
    last_succesful_mailing = state.get('last_succesful_mailing')

    if last_succesful_mailing:
        last_succesful_mailing = datetime.fromisoformat(last_succesful_mailing)
    else:
        last_succesful_mailing = yesterday

    return last_succesful_mailing


def main():
    path = 'sendler/app/state.json'

    last_succesful_mailing = get_last_successful_mailing(path)

    try:
        subscribers = get_subscribers()
        categories = get_categories()
        jobs_by_cat = get_jobs(categories, last_succesful_mailing)

    except httpx.HTTPStatusError as e:
        logger.error(e)
        sys.exit(1)
    else:
        data = {'last_succesful_mailing': datetime.now(pytz.utc).isoformat()}
        save_state(path, data)

    print(
        f'Total subscribers {len(subscribers)}, categories {len(jobs_by_cat)}, jobs {sum(len(jobs) for key, jobs in jobs_by_cat.items())}'
    )


if __name__ == '__main__':
    main()
