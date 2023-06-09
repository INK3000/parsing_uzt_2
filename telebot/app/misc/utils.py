import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from telebot.app import handlers

logger = logging.getLogger(__name__)


def get_handlers_list(handlers_module):
    handlers_list = []
    for handler_name in dir(handlers_module):
        if handler_name[:2] == "h_":
            handler = getattr(handlers_module, handler_name)
            handlers_list.append(handler)
    return handlers_list


def get_commands(handlers_module) -> dict:
    commands = dict()
    handlers_list = get_handlers_list(handlers_module)

    for handler in handlers_list:
        for item_name in dir(handler):
            if item_name[:4] == "cmd_":
                command = getattr(handler, item_name)
                command_name = item_name.split("_")[1]
                command_description = command.__doc__ or "No description"

                commands[command_name] = command_description.strip()
    return commands


async def set_commands(bot: Bot, bot_commands: dict):
    commands_list = []

    for command, description in bot_commands.items():
        commands_list.append(
            BotCommand(command=command, description=description.capitalize())
        )
    await bot.set_my_commands(commands=commands_list)


def add_routers(dp: Dispatcher, handlers_module):
    handlers_list = get_handlers_list(handlers_module)
    for handler in handlers_list:
        dp.include_router(handler.router)


def register_all_middlewares(dp: Dispatcher, middlewares: list):
    for middleware in middlewares:
        dp.update.middleware(middleware)


def register_all_outermiddlewares(dp: Dispatcher, middlewares: list):
    for middleware in middlewares:
        dp.update.outer_middleware(middleware)


async def on_start_bot(bot: Bot, bot_commands):
    await set_commands(bot, bot_commands)


async def on_stop_bot(bot: Bot):
    ...


# for add/remove subscriptions
