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

# Nothing required 
class Customer(BaseModel):
    name: constr(max_length=255)
    mobile: constr(max_length=15)
    email: constr(max_length=255)
    password_hash: constr(max_length=255)
    doctor_name: constr(max_length=255)
    class Config:
        arbitrary_types_allowed = True