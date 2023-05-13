from pydantic import BaseModel


class Subscription(BaseModel):
    category_id: int
    last_upd_id: int


class Subscriber(BaseModel):
    telegram_id: int
    subscriptions: list[Subscription] | None
