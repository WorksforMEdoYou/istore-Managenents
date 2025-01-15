from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class MedicineMasterBase(BaseModel):
    medicine_name: constr(max_length=255)
    generic_name: constr(max_length=255)
    hsn_code: constr(max_length=10)
    formulation: constr(max_length=50)
    strength: constr(max_length=50)
    unit_of_measure: constr(max_length=10)
    manufacturer_id: int
    category_id: int

class MedicineMasterCreate(MedicineMasterBase):
    pass

class MedicineMaster(MedicineMasterBase):
    medicine_id: Optional[int]

    class Config:
        from_attributes = True