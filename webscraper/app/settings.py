import re
from dataclasses import dataclass
from urllib.parse import urljoin

from environs import Env


@dataclass
class ApiSettings:
    base_url: str
    headers: dict


@dataclass
class TargetSettings:
    base_url: str
    start_url: str
    headers: dict


@dataclass
class Settings:
    target: TargetSettings
    api: ApiSettings


def get_headers(filename: str) -> dict:
    with open(filename, 'r') as file:
        pattern = re.compile(r'^(.*): (.*)')
        headers = dict()
        for line in file:
            m = re.match(pattern, line)
            if len(m.groups()) == 2:
                key, value = m.groups()
                headers[key] = value
    return headers


def get_settings():
    env = Env()
    env.read_env()

    api_headers = {
        'accept': 'application/json',
        'X-API-Key': env.str('API_KEY'),
    }

    target_headers = get_headers(env.str('UZT_HEADERS_PATH'))

    settings = Settings(
        target=TargetSettings(
            base_url=env.str('TARGET_BASE_URL'),
            start_url=env.str('TARGET_START_URL'),
            headers=target_headers,
        ),
        api=ApiSettings(base_url=env.str('API_BASE_URL'), headers=api_headers),
    )

    return settings


settings = get_settings()
