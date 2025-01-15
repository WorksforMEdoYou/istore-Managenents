from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class SubstituteBase(BaseModel):
    medicine_id: int
    substitute_medicine: constr(max_length=255)

class SubstituteCreate(SubstituteBase):
    pass

class Substitute(SubstituteBase):
    substitute_id: Optional[int]

    class Config:
        from_attributes = True