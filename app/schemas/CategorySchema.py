from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class CategoryBase(BaseModel):
    category_name: constr(max_length=255)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: Optional[int]

    class Config:
        from_attributes = True