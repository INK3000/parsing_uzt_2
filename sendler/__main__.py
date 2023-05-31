import cProfile
import json
import sys
from datetime import datetime, timedelta
from urllib.parse import quote_plus

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
    if resp.status_code == 200:
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
            settings.api.jobs.get.format(category.id, quote_plus(date)), Job
        )
        if jobs:
            jobs_by_cat[category.id] = jobs

    return jobs_by_cat


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


def save_state(path):
    data = {'last_succesful_mailing': datetime.now(pytz.utc).isoformat()}

    try:
        with open(path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        logger.error(e)


def get_last_successful_mailing(path):

    yesterday = datetime.now(pytz.utc) - timedelta(days=1)

    state = get_state(path)
    last_succesful_mailing = state.get('last_succesful_mailing')

    if not last_succesful_mailing:
        last_succesful_mailing = yesterday

    return last_succesful_mailing


def get_text(category_name: str, jobs_by_category: list[Job]):
    intro = f'{category_name}: \n\n'
    text = '\n'.join([str(job) for job in jobs_by_category])
    return intro + text


# def get_text_chunks(subscriber):
#     text_chunks = list()
#     for subscription in subscriber.subscriptions:
#         if jobs_by_cat.get(subscription)
#
#
#         ...
#     return text_chunks


# def get_mailing_list(subscribers: list[Subscriber]):
#
#     mailing_list = dict()
#     for subscriber in subscribers:
#         text_chanks = get_text_chunks(subscriber)
#         if text_chanks:
#             mailing_list[subscriber.telegram_id] = text_chanks
#
#     return mailing_list


def to_str_job(job: Job):
    return f'<a href="{job.url}">{job.title}</a> {job.company}'


def get_text_chunks(jobs: list[Job]) -> list[str]:
    start = 0
    range = 20
    text_chunks = []
    while start < len(jobs):

        text_list = list(
            [to_str_job(job) for job in jobs[start : start + range]]
        )
        joined_text = '\n'.join(text_list)
        text_chunks.append(joined_text)
        start = start + range
    return text_chunks


def get_text_by_category(jobs_by_category) -> dict[int, list[str]]:
    text_by_category = dict()
    for category, jobs in jobs_by_category.items():
        if jobs:
            text_by_category[category] = get_text_chunks(jobs)
    return text_by_category


def get_jobs_by_category(jobs_by_category):
    text_by_category = dict()
    for category_id, jobs in jobs_by_category.items():
        if not jobs:
            continue
        text_by_category[category_id] = get_text_chunks(jobs)

    return text_by_category


def main():
    path = 'sendler/app/state.json'

    last_succesful_mailing = get_last_successful_mailing(path)

    subscribers = get_subscribers()
    categories = get_categories()
    jobs_by_category = get_jobs(categories, last_succesful_mailing)

    # save_state(path)

    text_by_category = get_text_by_category(jobs_by_category)

    print(
        f'Total subscribers {len(subscribers)}, categories {len(jobs_by_category)}, jobs {sum(len(jobs) for key, jobs in jobs_by_category.items())}'
    )


if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    profiler.dump_stats('stats.txt')
