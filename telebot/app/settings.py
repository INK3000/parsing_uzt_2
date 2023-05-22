from dataclasses import dataclass
from urllib.parse import urljoin

import environs

from telebot.app import handlers


@dataclass
class Urls:
    get: str | None = None
    create: str | None = None
    update: str | None = None


@dataclass
class BotSettings:
    admin_id: int
    token: str


@dataclass
class APISettings:
    headers: dict
    user: Urls
    categories: Urls


@dataclass
class Settings:
    bot: BotSettings
    api: APISettings


# def get_commands(handlers) -> list[BotCommand]:
#     commands: list[BotCommand] = []
#
#     for handler_name in dir(handlers):
#         print(handler_name)
#         if handler_name[:2] == "h_":
#             handler = getattr(handlers, handler_name)
#
#             for item_name in dir(handler):
#                 if item_name[:4] == "cmd_":
#                     command = getattr(handler, item_name)
#                     commands.append(
#                         BotCommand(name=item_name, description=command.__doc__)
#                     )
#     return commands
#
#
# print(get_commands(handlers))


def get_settings():
    env = environs.Env()
    env.read_env()
    api_base_url = env.str("API_BASE_URL")
    bot = BotSettings(
        admin_id=env.int("TELEGRAM_ADMIN_ID"),
        token=env.str("BOT_TOKEN"),
    )

    api = APISettings(
        headers={"accept": "application/json"},
        user=Urls(
            get=urljoin(api_base_url, env.str("USER_GET_ENDPOINT")),
            create=urljoin(api_base_url, env.str("USER_CREATE_ENDPOINT")),
            update=urljoin(api_base_url, env.str("USER_UPDATE_ENDPOINT")),
        ),
        categories=Urls(get=urljoin(
            api_base_url, env.str("CATEGORIES_GET_ENDPOINT"))),
    )
    if not bot.token:
        raise Exception("BOT_TOKEN not loaded")
    return Settings(bot=bot, api=api)


settings = get_settings()
