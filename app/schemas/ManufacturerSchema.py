from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class ManufacturerBase(BaseModel):
    manufacturer_name: constr(max_length=255)

class ManufacturerCreate(ManufacturerBase):
    pass

class Manufacturer(ManufacturerBase):
    manufacturer_id: Optional[int]

    class Config:
        from_attributes = True