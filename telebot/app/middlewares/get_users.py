import json
import logging
from typing import Any

import httpx
from aiogram import BaseMiddleware
from app.pyd_models.subscriber import Subscriber

logger = logging.getLogger(__name__)

HEADERS = {"accept": "application/json"}


class GetUsers(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.subscribers: dict[int, Subscriber] = dict()

        def get_subsriber_from_inner_dict(user_id):
            return self.subscribers.get(user_id)

        def get_subscriber_from_api(user_id):
            url = f"http://localhost:8000/api/subscriber/{user_id}"
            try:
                response = httpx.get(url=url, headers=HEADERS)
                if response.status_code == 200:
                    return Subscriber(**response.json())
            except httpx.ConnectError as e:
                logger.error(f"Error to connection to {url}")

        def create_subscriber_for_api(user_id):
            url = "http://localhost:8000/api/subscriber/create"
            try:
                response = httpx.post(
                    url=url, content=json.dumps({"telegram_id": user_id})
                )
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

        subscriber = self.subscribers.get(user_id)

        for fn in self.fn_list:
            subscriber = fn(user_id)
            if subscriber:
                break

        if subscriber:
            self.subscribers[user_id] = subscriber
            data["subscriber"] = subscriber

        return await handler(event, data)
