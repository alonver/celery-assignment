from pydantic import BaseModel


class CategoryCreate(BaseModel):
    category_name: str
    region: str
    type: str
