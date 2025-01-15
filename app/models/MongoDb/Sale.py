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

# this require the medicine_id, batch id from stock

class SaleItem(BaseModel):
    medicine_id: int
    batch_id: str # this id should contain the stock id
    expiry_date: datetime
    quantity: int
    price: float
    class Config:
        arbitrary_types_allowed = True

class Sale(BaseModel):
    store_id: int
    sale_date: datetime
    customer_id: str  # Changed from int
    total_amount: float
    invoice_id: str
    sale_items: List[SaleItem]
    class Config:
        arbitrary_types_allowed = True