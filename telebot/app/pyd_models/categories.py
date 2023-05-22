from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str


class Categories(BaseModel):
    data: list[Category]
