from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
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

class OrderItem(BaseModel):
    medicine_id: int
    quantity: int
    price: float
    unit: str
    class Config:
        arbitrary_types_allowed = True

class OrderStatus(str, Enum):
    def __str__(self):
        return str(self.value)
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    def __str__(self):
        return str(self.value)
    ONLINE = "online"
    CASH = "cash"
    COD = "cod"

class Order(BaseModel):
    store_id: int
    customer_id: str # from customer id
    order_date: datetime
    order_status: OrderStatus  # "pending", "processing", "shipped", "delivered", "cancelled"
    payment_method: PaymentMethod  # "online", "cash", "cod"
    total_amount: float
    order_items: List[OrderItem]
    class Config:
        arbitrary_types_allowed = True

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
    invoice_id: int
    sale_items: List[SaleItem]
    class Config:
        arbitrary_types_allowed = True

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

class Pricing(BaseModel):
    store_id: int
    medicine_id: int
    price: float
    mrp: float
    discount: float
    net_rate: float
    is_active: bool
    last_updated_by: str # user id or name of the person who last updated
    updated_on: datetime
    class Config:
        arbitrary_types_allowed = True

class Customer(BaseModel):
    name: constr(max_length=255)
    mobile: constr(max_length=15)
    email: constr(max_length=255)
    password_hash: constr(max_length=255)
    doctor_name: constr(max_length=255)
    address: Text
    class Config:
        arbitrary_types_allowed = True

class MedicineAvailability(BaseModel):
    store_id: int
    medicine_id: int
    available_quantity: int
    last_updated: datetime
    updated_by: int
    class Config:
        arbitrary_types_allowed = True
    