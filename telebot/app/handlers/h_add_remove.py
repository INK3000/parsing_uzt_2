import logging
from datetime import datetime

import httpx
from aiogram import F, Router, types

from ..handlers import h_commands
from ..keyboards import subscriptions as kb
from ..pyd_models.categories import Category
from ..pyd_models.subscriber import Subscriber, Subscription
from ..settings import settings

logger = logging.getLogger(__name__)

router = Router()


async def close_keyboard(
    callback: types.CallbackQuery, subscriber, categories
):
    await callback.answer()
    await callback.message.delete()
    await h_commands.cmd_show(callback.message, subscriber, categories)


async def save_via_API(
    subscriber: Subscriber,
):
    url = settings.api.user.update
    try:
        assert url
        response = httpx.post(
            url=url, content=subscriber.json(), headers=settings.api.headers
        )
    except Exception as e:
        logger.error(
            f'The service is temporarily unavailable. Please try again in a few minutes'
        )


async def add_subscription(
    callback: types.CallbackQuery,
    subscriber: Subscriber,
    categories: list[Category],
):
    category_id = int(callback.data.split('_')[-1])
    subscriber.subscriptions.append(Subscription(category_id=category_id))
    await save_via_API(subscriber)
    await callback.answer()

    await callback.message.edit_text(
        text='Select categories to add and then press <b>Complete</b>',
        reply_markup=kb.get_subs_kbd(subscriber, categories, 'add'),
    )


async def remove_subscription(
    callback: types.CallbackQuery,
    subscriber: Subscriber,
    categories: list[Category],
):
    category_id = int(callback.data.split('_')[-1])

    assert subscriber.subscriptions
    [
        subscriber.subscriptions.remove(item)
        for item in subscriber.subscriptions
        if item.category_id == category_id
    ]
    await save_via_API(subscriber)
    await callback.answer()

    await callback.message.edit_text(
        text='Select categories to remove and then press <b>Complete</b>',
        reply_markup=kb.get_subs_kbd(subscriber, categories, 'remove'),
    )


async def alert(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer('alert!')


# register handlers
router.callback_query.register(
    close_keyboard, F.data.lower() == 'close_keyboard'
)
router.callback_query.register(add_subscription, F.data.startswith('add_'))
router.callback_query.register(
    remove_subscription, F.data.startswith('remove_')
)
