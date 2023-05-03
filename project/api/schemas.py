from ninja import ModelSchema, Schema

from .models import Category


# schemas for CategoryOfJob
class CategorySchemaOut(ModelSchema):
    class Config:
        model = Category
        model_fields = "__all__"


class CategorySchemaUpdate(Schema):
    id: int
    last_id: int


class CategorySchemaIn(ModelSchema):
    class Config:
        model = Category
        model_exclude = ["id"]


# schema for some errors output
class Error(Schema):
    detail: str
