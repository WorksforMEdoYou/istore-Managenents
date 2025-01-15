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

# this require store_id, medicine_id from the sql

class MedicineForms(str, Enum):
    def __str__(self):
        return str(self.value)
    LIQUID = "liquid"
    TABLET = "tablet"
    INJECTION = "injection"
    CAPSULE = "capsule"
    POWDER = "powder"

class UnitsInPack(str, Enum):
    def __str__(self):
        return str(self.value)
    ML = "ml"
    COUNT = "count"
    MGMS = "mgms"

class BatchDetails(BaseModel):
    expiry_date: datetime
    units_in_pack: UnitsInPack
    batch_quantity: int
    class config:
        arbitrary_types_allowed = True

class Stock(BaseModel):
    store_id: int
    medicine_id: int
    medicine_form: MedicineForms
    available_stock: int
    batch_detais: BatchDetails
    class Config:
        arbitrary_types_allowed = True