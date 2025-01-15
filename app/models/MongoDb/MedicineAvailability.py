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

# reuire the medicine id from mysql
class MedicineAvailability(BaseModel):
    store_id: int
    medicine_id: int
    available_quantity: int
    last_updated: datetime
    updated_by: int
    class Config:
        arbitrary_types_allowed = True
        