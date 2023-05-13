from aiogram import types
from app.pyd_models.subscriber import Subscriber
from httpx import Response


async def cmd_start(message: types.Message, subscriber: Subscriber | None = None):
    if not subscriber:
        await message.answer(
            text="The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        await message.answer(text=f"{subscriber.telegram_id}")

    # await message.answer(
    #                text="/start - if something wrong - try start again \n"
    #     "/add - add categories to my subscribes\n"
    #     "/remove - remove categories from my subscribes\n"
    #     "/show - show my subscribes"
    # )
