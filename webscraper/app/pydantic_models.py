from typing import Any

from pydantic import BaseModel


class FResp(BaseModel):
    ok: bool = False
    data: Any = ""

    def __bool__(self):
        return self.ok


class Job(BaseModel):
    date_from: str
    date_to: str
    title: str
    company: str
    place: str
    url: str


class CategoryIn(BaseModel):
    id: int
    name: str
    href: str
    last_id: int | None


class CategoryOut(BaseModel):
    name: str
    href: str


class CategoryUpd(BaseModel):
    id: int
    last_id: int
