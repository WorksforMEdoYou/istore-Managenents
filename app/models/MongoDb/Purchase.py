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

# this takes the batch id from the stock mongodb, 
# medicine_id, store_id, and manufacture_id from the mysql

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
    
class Package(str, Enum):
    def __str__(self):
        return str(self.value)
    STRIP = "strip"
    BOTTLE = "bottle"
    VIAL = "vial"
    AMP = "amp"
    SACHET = "sachet"

class PurchaseItem(BaseModel):
    medicine_id: int
    batch_id: str  #from batch details
    expiry_date: str
    quantity: int
    price: float
    manufacture_id: int
    medicine_form: MedicineForms
    units_in_pack: UnitsInPack
    unit_quantity: int # n
    package: Package # strip/bottle/vial/amp/sachet
    package_count: int # p
    medicine_quantity: int #n*p
    class Config:
        arbitrary_types_allowed = True

class Purchase(BaseModel):
    store_id: int
    purchase_date: datetime
    distributor_id: int
    total_amount: float
    invoice_number : int
    purchase_items: List[PurchaseItem]
    class Config:
        arbitrary_types_allowed = True