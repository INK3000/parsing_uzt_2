import datetime
from typing import Any

from pydantic import BaseModel


class Job(BaseModel):
    date_scraped: datetime.datetime
    date_from: str
    date_to: str
    title: str
    company: str
    place: str
    url: str


class Category(BaseModel):
    id: int
    name: str


class Subscription(BaseModel):
    category_id: int


class Subscriber(BaseModel):
    telegram_id: int
    subscriptions: list[Subscription | None]


class SendlerData(BaseModel):
    data: datetime.datetime
    status: bool
    details: str
