import logging
from typing import Any

import httpx
from aiogram import BaseMiddleware

from ..pyd_models.categories import Category
from ..settings import settings

logger = logging.getLogger(__name__)


class GetCategories(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.categories: list[Category] = []

        def get_categories_from_inner_dict():
            if self.categories:
                return self.categories

        def get_categories_from_api():
            # see .env file for endpoints
            url = settings.api.categories.get
            headers = settings.api.headers
            try:
                assert url
                response = httpx.get(url=url, headers=headers)
                if response.status_code != 200:
                    response.raise_for_status()
                return [Category(**item) for item in response.json()]
            except (httpx.ConnectError, httpx.HTTPStatusError) as e:
                logger.error(e)

        self.fn_list = [
            get_categories_from_inner_dict,
            get_categories_from_api,
        ]

    async def __call__(self, handler, event, data: dict[str, Any]):
        categories = None
        data['categories'] = None
        for fn in self.fn_list:
            categories = fn()
            if categories:
                self.categories = categories
                data['categories'] = categories
                break

        return await handler(event, data)
