from dataclasses import dataclass
from urllib.parse import urljoin

import environs


@dataclass
class Endpoints:
    get: str


@dataclass
class ApiSettings:
    headers: dict
    categories: Endpoints
    jobs: Endpoints
    subscribers: Endpoints


@dataclass
class BotSettings:
    base_url: str


@dataclass
class Settings:
    bot: BotSettings
    api: ApiSettings


def get_settings():
    env = environs.Env()
    env.read_env()
    api_base_url = env.str('API_BASE_URL')

    settings = Settings(
        bot=BotSettings(
            base_url=f'https://api.telegram.org/bot{env.str("BOT_API_TOKEN")}'
        ),
        api=ApiSettings(
            headers={
                'accept': 'application/json',
                'X-API-Key': env.str('API_KEY'),
            },
            categories=Endpoints(get=urljoin(api_base_url, 'api/categories')),
            jobs=Endpoints(
                get=urljoin(api_base_url, 'api/category/{}/jobs?from_date={}')
            ),
            subscribers=Endpoints(
                get=urljoin(api_base_url, 'api/subscribers')
            ),
        ),
    )
    return settings


settings = get_settings()
