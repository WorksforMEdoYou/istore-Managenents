from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List
from datetime import datetime
from app.models.MongoDb.Eunums import MedicineForms, UnitsInPack

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

class BatchDetails(BaseModel):
    expiry_date: datetime = Field(..., description="Expity date of the batch medicines")
    units_in_pack: UnitsInPack = Field(..., description="Units In Pack for the batch medicines")
    batch_quantity: int = Field(..., description="Batch quantity of the batch medicines")
    batch_number: constr(max_length=255) = Field(..., description="Batch number for the medicines") # added new field according to the review
    class config:
        arbitrary_types_allowed = True

class Stock(BaseModel):
    
    """
    Base model for the Stock collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    medicine_form: MedicineForms = Field(..., description="Medicine form can liquid, tablet, injuction, capsule, powder")
    available_stock: int = Field(..., description="Available stock of total medicines in batchs")
    batch_detais: BatchDetails = Field(..., description="batch details")
    class Config:
        arbitrary_types_allowed = True