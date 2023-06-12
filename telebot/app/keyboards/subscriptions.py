from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..pyd_models.categories import Category
from ..pyd_models.subscriber import Subscriber


def get_subs_kbd(
    subscriber: Subscriber, categories: list[Category], action: str
):
    added_list = [item.category_id for item in subscriber.subscriptions]
    filters = {
        'add': lambda item: item.id not in added_list,
        'remove': lambda item: item.id in added_list,
    }
    filtered_categories = filter(filters.get(action), categories)
    builder = InlineKeyboardBuilder()
    [
        builder.add(
            types.InlineKeyboardButton(
                text=item.name, callback_data=f'{action}_{item.id}'
            )
        )
        for item in filtered_categories
    ]
    builder.add(
        types.InlineKeyboardButton(
            text='[ Hide categories ]', callback_data='close_keyboard'
        )
    )
    builder.adjust(1, repeat=True)
    return builder.as_markup()
