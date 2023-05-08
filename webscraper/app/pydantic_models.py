from typing import Any

from pydantic import BaseModel


class FResp(BaseModel):
    status_ok: bool = False
    data: Any = ""

    def __bool__(self):
        return self.status_ok


class Job(BaseModel):
    date1: str
    date2: str
    title: str
    company: str
    place: str


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
