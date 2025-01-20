from bson import ObjectId
from pydantic import BaseModel, Field, constr
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

class MedicineAvailability(BaseModel):
    
    """
    Base model for the Medicine Availability collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    available_quantity: int = Field(..., description="Medicine Availabiliry for the particular medicine")
    last_updated: datetime = Field(..., description="Last Updated")
    updated_by: constr(max_length=255) = Field(..., description="Updated by Either can be a User_id or user_name from the MYSQL user table")
    class Config:
        arbitrary_types_allowed = True
        