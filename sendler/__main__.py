import json
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin

import betterlogging as logging
import httpx
import pytz
from rich.progress import track

from .app.pydantic_models import (
    Category,
    Job,
    Subscriber,
    LastSuccessfulSendDetail,
)
from .app.settings import settings

# import logging
logger = logging.getLogger('sendler')
logging.basic_colorized_config(level=logging.INFO)


def get_data_from_api(endpoint, data_class):
    data = list()
    resp = httpx.get(url=endpoint, headers=settings.api.headers)
    if resp.status_code == 200:
        if isinstance(resp.json(), list):
            for item in resp.json():
                data.append(data_class(**item))
        else:
            data.append(data_class(**resp.json()))
    return data


def post_data_to_api(endpoint, data_class, payload=None):
    data = list()
    resp = httpx.post(url=endpoint, headers=settings.api.headers, data=payload)
    if resp.status_code == 201:
        if isinstance(resp.json(), list):
            for item in resp.json():
                data.append(data_class(**item))
        else:
            data.append(data_class(**resp.json()))
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
            settings.api.jobs.get.format(category.id, date), Job
        )
        if jobs:
            jobs_by_cat[category.id] = jobs

    return jobs_by_cat


def get_last_successful_send_detail() -> list[LastSuccessfulSendDetail]:
    data = get_data_from_api(
        settings.api.last_successful_send_detail.get, LastSuccessfulSendDetail
    )
    return data


def create_last_successful_send_detail() -> list[LastSuccessfulSendDetail]:
    data = post_data_to_api(
        settings.api.last_successful_send_detail.post, LastSuccessfulSendDetail
    )
    return data



def get_last_successful_mailing():

    last_successful_send_detail = get_last_successful_send_detail()
    if last_successful_send_detail:
        last_succesful_mailing = last_successful_send_detail[0].timestamp
        print(last_succesful_mailing, 'from api')
    else:
        yesterday = datetime.now(pytz.utc) - timedelta(days=1)
        last_succesful_mailing = datetime.isoformat(yesterday)
        print(last_succesful_mailing, 'from local')
   
    return last_succesful_mailing


def save_last_successful_mailing():
    last_successful_send_detail = create_last_successful_send_detail()
    if not last_successful_send_detail:
        raise Exception("Last successful send detail has not been created")


def to_str_job(job: Job):
    return f'<a href="{job.url}">{job.title}</a> {job.company}'


def get_chunks(lst: list, chunk_size: int):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_text_chunks(jobs: list[Job]) -> list[str]:
    text_list = list([to_str_job(job) for job in jobs])
    text_chunks = list('\n'.join(chunk) for chunk in get_chunks(text_list, 20))
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
    for subscriber in track(subscribers):
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
    last_succesful_mailing = get_last_successful_mailing()
    try:
        subscribers = get_subscribers()
        categories = get_categories()
        jobs_by_category = get_jobs(categories, last_succesful_mailing)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    text_by_category = get_text_by_category(jobs_by_category)
    logger.info('All data is prepared')
    logger.info(
        f'Total subscribers {len(subscribers)}, jobs {sum(len(jobs) for jobs in jobs_by_category.values())} in {len(jobs_by_category)} categories'
    )
    logger.info('Start the mailing...')
    try:
        mailing_all(subscribers, text_by_category, categories)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    else:
        try:
            save_last_successful_mailing() 
        except Exception as e:
            logger.error(e)
            sys.exit(1)
    logger.info('The mailing has been done')


if __name__ == '__main__':
    main()
