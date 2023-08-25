from dataclasses import dataclass
from urllib.parse import urljoin

import environs


@dataclass
class Endpoint:
    get: str
    post: str | None = None


@dataclass
class ApiSettings:
    headers: dict
    categories: Endpoint
    jobs: Endpoint
    subscribers: Endpoint
    last_successful_send_detail: Endpoint


@dataclass
class BotSettings:
    base_url: str


@dataclass
class Settings:
    bot: BotSettings
    api: ApiSettings
    state_path: str


def get_settings():
    env = environs.Env()
    env.read_env()
    api_base_url = env.str('API_BASE_URL')

    settings = Settings(
        bot=BotSettings(
            base_url=f'https://api.telegram.org/bot{env.str("BOT_API_TOKEN")}/'
        ),
        api=ApiSettings(
            headers={
                'accept': 'application/json',
                'X-API-Key': env.str('API_KEY'),
            },
            categories=Endpoint(get=urljoin(api_base_url, 'api/categories')),
            jobs=Endpoint(
                get=urljoin(api_base_url, 'api/category/{}/jobs?from_date={}')
            ),
            subscribers=Endpoint(
                get=urljoin(api_base_url, 'api/subscribers')
            ),
            last_successful_send_detail=Endpoint(
                get=urljoin(
                    api_base_url, 'api/last-successful-send'
                ),
                post=urljoin(
                    api_base_url, 'api/last-successful-send/create'
                )
            )

        ),
        state_path=env.str('STATE_PATH'),
    )
    return settings


settings = get_settings()
