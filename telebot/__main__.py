import asyncio

import betterlogging as logging
from aiogram import Bot, Dispatcher

from .app import handlers
from .app.middlewares.get_categories import GetCategories
from .app.middlewares.get_users import GetUsers
from .app.misc import utils
from .app.settings import settings

# import logging
logger = logging.getLogger(__name__)
logging.basic_colorized_config(level=logging.INFO)


async def main():
    bot = Bot(token=settings.bot.token, parse_mode='HTML')
    dp = Dispatcher()

    dp.startup.register(utils.on_start_bot)
    dp.shutdown.register(utils.on_stop_bot)
    utils.add_routers(dp, handlers)

    utils.register_all_middlewares(dp, [])
    utils.register_all_outermiddlewares(dp, [GetUsers(), GetCategories()])

    await bot.delete_webhook(drop_pending_updates=True)

    # for all functions in the handlers, register them if they have the prefix cmd_
    # and add the description from the docstring
    await dp.start_polling(bot, bot_commands=utils.get_commands(handlers))


if __name__ == '__main__':
    asyncio.run(main())
