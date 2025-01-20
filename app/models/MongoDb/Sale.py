from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

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
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    batch_id: str = Field(..., description="Batch ObjectID from the stock ObjectID") # this id should contain the stock id
    expiry_date: datetime = Field(..., description="Expiry date of a medicine")
    quantity: int = Field(..., description="Quantity of the medicine")
    price: float = Field(..., description="Price of the medicine")
    class Config:
        arbitrary_types_allowed = True

class Sale(BaseModel):
    
    """
    Base model for the Sale collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    sale_date: datetime = Field(..., description="Sale Date")
    customer_id: str = Field(..., description="Customer OBjectId from the customer collection") 
    total_amount: float = Field(..., description="Total amount of the saled medicine")
    invoice_id: str = Field(..., description="invoice ID of the bill")
    sale_items: List[SaleItem] = Field(..., description="List of Saled medicines")
    class Config:
        arbitrary_types_allowed = True