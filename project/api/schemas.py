from ninja import ModelSchema, Schema

from . import models


# schemas for CategoryOfJob
class CategoryOut(ModelSchema):
    class Config:
        model = models.Category
        model_fields = "__all__"


class CategoryUpdate(Schema):
    id: int
    last_id: int


class CategoryIn(ModelSchema):
    class Config:
        model = models.Category
        model_exclude = ["id"]


# schemas for Subscribers
class SubscriberOut(ModelSchema):
    class Config:
        model = models.Subscriber
        model_fields = "__all__"


class SubscriberUpdate(Schema):
    id: int
    subscribed_to: str


class SubscriberIn(ModelSchema):
    class Config:
        model = models.Subscriber
        model_exclude = ["id"]


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
        model_exclude = ["id", "category", "date_upd"]


class JobListIn(Schema):
    data: list[JobIn]
