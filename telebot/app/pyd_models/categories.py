from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    last_upd_id: int | None
    

class Categories(BaseModel):
    data: list[Category]
    
