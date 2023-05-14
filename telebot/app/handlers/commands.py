from aiogram import types
from app.pyd_models.categories import Category
from app.pyd_models.subscriber import Subscriber
from httpx import Response


def format_my_categories(categories: list[Category]) -> str:
    formated_text = "You are not subscribed to any categories."
    intro = "You are subscribed to categories: \n"

    if categories:
        formated_text = intro + \
            "\n".join([category.name for category in categories])

    return formated_text


async def cmd_start(message: types.Message, **kwargs):
    subscriber: Subscriber | None = kwargs.get("subscriber")

    if not subscriber:
        await message.answer(
            text="The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        await message.answer(
            text="/show - show my subscribes\n"
            "/add - add categories to my subscribes\n"
            "/remove - remove categories from my subscribes\n"
            "/start - if something wrong - try restart"
        )


async def cmd_show(message: types.Message, **kwargs):
    subscriber: Subscriber | None = kwargs.get("subscriber")
    print(subscriber)

    if not subscriber:
        await message.answer(
            text=f"The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        text = format_my_categories(subscriber.subscriptions)
        await message.answer(text=text)
