import logging

from aiogram import Dispatcher

from ..pyd_models.categories import Category
from ..pyd_models.subscriber import Subscription

logger = logging.getLogger(__name__)


def subscriptions_to_text(
    subscriptions: list[Subscription], categories: list[Category]
) -> str:
    formated_text = 'You are not subscribed to any categories.'
    intro = 'You are subscribed to categories: \n\n'
    subscribed_ids = [item.category_id for item in subscriptions]
    if subscriptions:
        formated_text = intro + '\n'.join(
            [item.name for item in categories if item.id in subscribed_ids]
        )

    return formated_text
