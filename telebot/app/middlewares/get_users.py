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

    async def __call__(self, handler, event, data: dict[str, Any]):
        user_id = data.get("event_from_user").id

        subscriber = self.subscribers.get(user_id)

        if not subscriber:
            subscriber = self.get_subscriber_from_api(user_id)
        if not subscriber:
            subscriber = self.create_subscriber_for_api(user_id)

        if not subscriber:
            data["api_error"] = True
            return await handler(event, data)

        self.subscribers[user_id] = subscriber

        data["subscriber"] = subscriber
        data["api_error"] = False

        return await handler(event, data)

    @staticmethod
    def get_subscriber_from_api(user_id):
        url = f"http://localhost:8000/api/subscriber/{user_id}"
        try:
            response = httpx.get(url=url, headers=HEADERS)
            if response.status_code == 200:
                return Subscriber(**response.json())
        except httpx.ConnectError as e:
            logger.error(f"Error to connection to {url}")

    @staticmethod
    def create_subscriber_for_api(user_id):
        url = "http://localhost:8000/api/subscriber/create"
        try:
            response = httpx.post(
                url=url, content=json.dumps({"telegram_id": user_id}))
            if response.status_code == 201:
                return Subscriber(**response.json())
            if response.status_code == 200 and response.json():
                return Subscriber(**response.json())
        except Exception as e:
            logger.error(f"Error to connection to {url}")
