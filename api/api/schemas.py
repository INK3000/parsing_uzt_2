import datetime
from typing import Any

from ninja import ModelSchema, Schema

from . import models


# schemas for CategoryOfJob
class CategoryOut(ModelSchema):
    class Config:
        model = models.Category
        model_fields = "__all__"


class CategoryUpdate(Schema):
    last_upd_id: int


class CategoryIn(ModelSchema):
    class Config:
        model = models.Category
        model_exclude = ["id"]


# schemas for Subscribers
class SubscribedTo(Schema):
    category_id: int
    date_last_sent: datetime.datetime


class SubscriberOut(ModelSchema):
    subscriptions: list[SubscribedTo] | None

    class Config:
        model = models.Subscriber
        model_exclude = ["subscribed_to"]


class SubscriberIn(ModelSchema):
    class Config:
        model = models.Subscriber
        model_exclude = ["id", "date_created", "subscribed_to"]


class SubscriberUpdate(ModelSchema):
    subscriptions: list[SubscribedTo]

    class Config:
        model = models.Subscriber
        model_exclude = ["id", "date_created", "subscribed_to"]


# schema for some errors output
class Error(Schema):
    detail: str


# schemas for Jobs
class JobOut(ModelSchema):
    class Config:
        model = models.Job
        model_fields = "__all__"


class JobIn(ModelSchema):
    class Config:
        model = models.Job
        model_exclude = ["id", "category", "date_scraped"]


class JobListIn(Schema):
    data: list[JobIn]
