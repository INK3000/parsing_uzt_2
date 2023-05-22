import logging
from typing import Any

import httpx
from aiogram import BaseMiddleware

from telebot.app.pyd_models.subscriber import Subscriber
from telebot.app.settings import settings

logger = logging.getLogger(__name__)


class GetUsers(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.subscribers: dict[int, Subscriber] = dict()

        def get_subsriber_from_inner_dict(user_id):
            return self.subscribers.get(user_id)

        def get_subscriber_from_api(user_id):
            # see .env file for endpoints
            url = settings.api.user.get.format(user_id)
            try:
                response = httpx.get(url=url)
                if response.status_code == 200:
                    return Subscriber(**response.json())
            except httpx.ConnectError as e:
                logger.error(f"Error to connection to {url}")

        def create_subscriber_for_api(user_id):
            # see .env file for endpoints
            url = settings.api.user.create.format(user_id)
            try:
                response = httpx.get(url=url)
                if response.status_code == 201:
                    return Subscriber(**response.json())
                if response.status_code == 200 and response.json():
                    return Subscriber(**response.json())
            except Exception as e:
                logger.error(f"Error to connection to {url}")

        self.fn_list = [
            get_subsriber_from_inner_dict,
            get_subscriber_from_api,
            create_subscriber_for_api,
        ]

    async def __call__(self, handler, event, data: dict[str, Any]):
        user_id = data.get("event_from_user").id
        data["subscriber"] = None
        subscriber = self.subscribers.get(user_id)

        for fn in self.fn_list:
            subscriber = fn(user_id)
            if subscriber:
                self.subscribers[user_id] = subscriber
                data["subscriber"] = subscriber
                break

        return await handler(event, data)
