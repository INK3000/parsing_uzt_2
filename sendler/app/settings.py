from dataclasses import dataclass
from urllib.parse import urljoin

import environs


@dataclass
class Endpoints:
    get: str


@dataclass
class ApiSettings:
    api_key: str
    categories: Endpoints
    jobs: Endpoints
    users: Endpoints


@dataclass
class BotSettings:
    base_url: str


@dataclass
class Settings:
    bot: BotSettings
    api: ApiSettings


def get_settings():
    env = environs.Env()
    env.read()
    api_base_url = env.str('API-BASE-URL')

    settings = Settings(
        bot=BotSettings(
            base_url=f'https://api.telegram.org/bot{env.str("BOT-API-TOKEN")}'
        ),
        api=ApiSettings(
            api_key=env.str('API-KEY'),
            categories=Endpoints(get=urljoin(api_base_url, 'api/categories')),
            jobs=Endpoints(get=urljoin(api_base_url, 'api/category/{}/jobs')),
            users=Endpoints(get=urljoin(api_base_url, 'api/subscribers')),
        ),
    )
    return settings


settings = get_settings()
