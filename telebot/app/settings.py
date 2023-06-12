from dataclasses import dataclass
from urllib.parse import urljoin

import environs


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


def get_settings():
    env = environs.Env()
    env.read_env()
    api_base_url = env.str('API_BASE_URL')
    bot = BotSettings(
        admin_id=env.int('TELEGRAM_ADMIN_ID'),
        token=env.str('BOT_TOKEN'),
    )

    api = APISettings(
        headers={
            'accept': 'application/json',
            'X-API-Key': env.str('API_KEY'),
        },
        user=Urls(
            get=urljoin(api_base_url, env.str('USER_GET_ENDPOINT')),
            create=urljoin(api_base_url, env.str('USER_CREATE_ENDPOINT')),
            update=urljoin(api_base_url, env.str('USER_UPDATE_ENDPOINT')),
        ),
        categories=Urls(
            get=urljoin(api_base_url, env.str('CATEGORIES_GET_ENDPOINT'))
        ),
    )
    if not bot.token:
        raise Exception('BOT_TOKEN not loaded')
    return Settings(bot=bot, api=api)


settings = get_settings()
