from bson import ObjectId
from pydantic import BaseModel, Field
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

#require the store_id, medicine_id from the sql
class Pricing(BaseModel):
    
    """
    Base model for the pricing collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="medicine ID from the MYSQL medicine_mastrer table")
    price: float = Field(..., description="Price of the Medicine")
    mrp: float = Field(..., description="MRP of the medicine")
    discount: float = Field(..., description="Discount of the Medicine")
    net_rate: float = Field(..., description="NET Rate of the medicine")
    is_active: bool = Field(..., description="Is Active True or False")
    last_updated_by: str = Field(..., description="Last Updated can be a user_name or user_id from the MYSQL user table") # user id or name of the person who last updated
    updated_on: datetime = Field(..., description="updated on")
    class Config:
        arbitrary_types_allowed = True
         