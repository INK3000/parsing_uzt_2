import json
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin

import betterlogging as logging
import httpx
import progressbar
import pytz
from rich import print

from sendler.app.pydantic_models import Category, Job, Subscriber
from sendler.app.settings import settings

# import logging
logger = logging.getLogger('sendler')
logging.basic_colorized_config(level=logging.ERROR)


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


def get_last_successful_mailing(path: str):

    yesterday = datetime.now(pytz.utc) - timedelta(days=1)

    state = get_state(path)
    last_succesful_mailing = state.get('last_succesful_mailing')

    if not last_succesful_mailing:
        last_succesful_mailing = datetime.isoformat(yesterday)

    return last_succesful_mailing


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


def send_message(telegram_id: int, message: str):
    url = urljoin(settings.bot.base_url, 'sendMessage')
    data = {'chat_id': telegram_id, 'parse_mode': 'HTML', 'text': message}
    resp = httpx.post(url=url, data=data)
    time.sleep(1)
    return resp.status_code


def mailing_all(
    subscribers: list[Subscriber],
    text_by_category: dict[int, list[str]],
    categories: list[Category],
):
    bar = progressbar.ProgressBar()
    for subscriber in bar(subscribers):
        for subscription in subscriber.subscriptions:
            if text_by_category.get(subscription.category_id):
                category = next(
                    filter(
                        lambda c: c.id == subscription.category_id, categories
                    )
                )
                intro = f'<b>{category.name}</b> \n\n'
                for text_chunk in text_by_category[subscription.category_id]:
                    send_message(subscriber.telegram_id, intro + text_chunk)
                    intro = ''


def main():
    path = 'sendler/app/state.json'

    last_succesful_mailing = get_last_successful_mailing(path)

    try:
        subscribers = get_subscribers()
        categories = get_categories()
        jobs_by_category = get_jobs(categories, last_succesful_mailing)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    text_by_category = get_text_by_category(jobs_by_category)
    print('All data is prepared')
    print(
        f'Total subscribers {len(subscribers)}, jobs {sum(len(jobs) for jobs in jobs_by_category.values())} in {len(jobs_by_category)} categories'
    )
    print('Start mailing...')
    try:
        mailing_all(subscribers, text_by_category, categories)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    else:
        save_state(path)
    print('Mailing is done')


if __name__ == '__main__':
    main()
