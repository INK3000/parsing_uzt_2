import json
import logging
from typing import Any

import httpx
from aiogram import BaseMiddleware
from app.pyd_models.categories import Category

logger = logging.getLogger(__name__)

HEADERS = {"accept": "application/json"}


class GetCategories(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.categories: dict[int, Category] = dict()

        def get_categories_from_inner_dict():
            if self.categories:
                return self.categories

        def get_categories_from_api():
            url = "http://localhost:8000/api/categories"
            try:
                response = httpx.get(url=url, headers=HEADERS)
                if response.status_code == 200:
                    return {item["id"]: Category(**item) for item in response.json()}
            except httpx.ConnectError as e:
                logger.error(f"Error to connection to {url}")

        self.fn_list = [get_categories_from_inner_dict,
                        get_categories_from_api]

    async def __call__(self, handler, event, data: dict[str, Any]):
        categories = None

        for fn in self.fn_list:
            categories = fn()
            if categories:
                break

        if categories:
            self.categories = categories
            data["categories"] = categories

        return await handler(event, data)
