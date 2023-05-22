import logging

from aiogram import Bot, Router
from aiogram import filters as flt
from aiogram import types
from aiogram.fsm.context import FSMContext
from rich import print

from telebot.app.keyboards import subscriptions as kb
from telebot.app.misc import functions as fn
from telebot.app.misc.states import ManageSubscriptions
from telebot.app.pyd_models.categories import Category
from telebot.app.pyd_models.subscriber import Subscriber, Subscription

logger = logging.getLogger(__name__)

router = Router()


async def cmd_start(
    message: types.Message, subscriber: Subscriber, bot: Bot, state: FSMContext
):
    """
    If something went wrong, try start again
    """
    print(await state.get_state())
    if not subscriber:
        await message.answer(
            text="The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        commands = await bot.get_my_commands()
        text = "\n".join(
            [
                f"<b>/{command.command}</b>: {command.description}"
                for command in commands
            ]
        )
        await message.answer(text=text)


async def cmd_show(
    message: types.Message, subscriber: Subscriber, categories: list[Category]
):
    """Show my subscriptions"""
    if not subscriber:
        await message.answer(
            text=f"The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        subscriptions = subscriber.subscriptions
        text = fn.subscriptions_to_text(subscriptions, categories)
        await message.answer(text=text)


async def cmd_add_subscriptions(
    message: types.Message,
    subscriber: Subscriber,
    categories: list[Category],
):
    """Add to my subscriptions"""
    if not subscriber:
        await message.answer(
            text="The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        await message.answer(
            text="Select categories to add and then press <b>Complete</b>",
            reply_markup=kb.get_subs_kbd(subscriber, categories, "add"),
        )


async def cmd_remove_subscriptions(
    message: types.Message,
    subscriber: Subscriber,
    categories: list[Category],
):
    """Remove from my subscriptions"""
    if not subscriber:
        await message.answer(
            text="The service is temporarily unavailable. Please try again in a few minutes"
        )
    else:
        await message.answer(
            text="Select categories to remove and then press <b>Complete</b>",
            reply_markup=kb.get_subs_kbd(subscriber, categories, "remove"),
        )


async def cmd_showinfo(message: types.Message, bot: Bot, state: FSMContext):
    """
    Do you want some info?
    """
    info = str(dir(state))
    await message.answer(text=info)


# register all handlers ========================================
router.message.register(cmd_start, flt.Command("start"))
router.message.register(cmd_show, flt.Command("show"))
router.message.register(cmd_add_subscriptions, flt.Command("add"))
router.message.register(cmd_remove_subscriptions, flt.Command("remove"))
router.message.register(cmd_showinfo, flt.Command("showinfo"))
