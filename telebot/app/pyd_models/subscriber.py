import datetime

from pydantic import BaseModel


class Subscription(BaseModel):
    category_id: int
    date_last_sent: datetime.datetime


class Subscriber(BaseModel):
    telegram_id: int
    subscriptions: list[Subscription] | None
