import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from app import settings
from app.handlers import commands
from app.middlewares.get_users import GetUsers


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp.update.middleware.register(GetUsers())
    dp.message.register(commands.cmd_start, Command(commands=["start"]))
    dp.message.register(commands.cmd_show, Command(commands=["show"]))

    await dp.start_polling(bot)

    ...


if __name__ == "__main__":
    asyncio.run(main())
