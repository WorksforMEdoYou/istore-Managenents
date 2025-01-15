from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List
from datetime import datetime
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

#require the store_id, medicine_id from the sql
class Pricing(BaseModel):
    store_id: int
    medicine_id: int
    price: float
    mrp: float
    discount: float
    net_rate: float
    is_active: bool
    last_updated_by: str # user id or name of the person who last updated
    updated_on: datetime
    class Config:
        arbitrary_types_allowed = True
         