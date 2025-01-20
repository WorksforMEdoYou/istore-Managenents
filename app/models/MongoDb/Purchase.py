from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.models.MongoDb.Eunums import MedicineForms, UnitsInPack, Package

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

class PurchaseItem(BaseModel):
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    batch_id: str = Field(..., description="Batch ObjectID from the Sales collection")  #from batch details
    expiry_date: str = Field(..., description="Expiry date of the purchased medicine")
    quantity: int = Field(..., description="Quantity of the Purchased Medicine")
    price: float = Field(..., description="Price of the Purchased medicine ")
    manufacture_id: int = Field(..., description="Manufacturer ID from the MYSQL manufaccturer table")
    medicine_form: MedicineForms = Field(..., description="Medicine Form can be liquid, tablet, injection, capsule, powder")
    units_in_pack: UnitsInPack = Field(..., description="Units In Pack can be Ml Count MGMS")
    unit_quantity: int = Field(..., description="Unit Quantity") # n
    package: Package = Field(..., description="Package can be strip, bottle, vial, amp, sachet") # strip/bottle/vial/amp/sachet
    package_count: int = Field(..., description="Package count") # p
    medicine_quantity: int = Field(..., description="Medicine can be a multiple of unit_quantity * package_count") #n*p
    class Config:
        arbitrary_types_allowed = True

class Purchase(BaseModel):
    
    """
    Base model for the Purchase collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    purchase_date: datetime = Field(..., description="Purchase Date of the medicines")
    distributor_id: int = Field(..., description="Distributor ID from the MYSQL distributor table")
    total_amount: float = Field(..., description="Total Amount of the purchased medicines")
    invoice_number : int = Field(..., description="Invoice Number of the purchase bill")
    purchase_items: List[PurchaseItem] = Field(..., description="Purchase items list")
    class Config:
        arbitrary_types_allowed = True