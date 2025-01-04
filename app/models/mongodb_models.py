#mongodb_models.py
from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ObjectIdField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, ObjectId)):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v) if isinstance(v, str) else v

class OrderItem(BaseModel):
    medicine_id: int
    quantity: int
    price: float
    unit: str
    class Config:
        arbitrary_types_allowed = True

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    ONLINE = "online"
    CASH = "cash"
    COD = "cod"


class Order(BaseModel):
    store_id: int
    customer_id: int
    order_date: datetime
    order_status: OrderStatus  # "pending", "processing", "shipped", "delivered", "cancelled"
    payment_method: PaymentMethod  # "online", "cash", "cod"
    total_amount: float
    order_items: List[OrderItem]
    class Config:
        arbitrary_types_allowed = True

class SaleItem(BaseModel):
    medicine_id: int
    batch_id: int
    quantity: int
    price: float
    class Config:
        arbitrary_types_allowed = True

class Sale(BaseModel):
    store_id: int
    sale_date: datetime
    customer_id: int
    total_amount: float
    invoice_id: int
    sale_items: List[SaleItem]
    class Config:
        arbitrary_types_allowed = True

class Stock(BaseModel):
    medicine_id: int
    manufacturer_id: int
    distributor_id: int
    expiry_date: datetime
    available_stock: int
    mrp: float
    batches: List[int]
    discount: float
    net_rate: float
    units_per_pack: int
    units_per_pack_uom: constr(max_length=10)
    class Config:
        arbitrary_types_allowed = True

class PurchaseItem(BaseModel):
    medicine_id: int
    batch_id: int
    quantity: int
    price: float
    units_per_pack: int
    units_per_pack_uom: constr(max_length=10)
    class Config:
        arbitrary_types_allowed = True

class Purchase(BaseModel):
    store_id: int
    purchase_date: datetime
    distributor_id: int
    total_amount: float
    purchase_items: List[PurchaseItem]
    class Config:
        arbitrary_types_allowed = True

class Customer(BaseModel):
    name: constr(max_length=255)
    mobile: constr(max_length=15)
    email: constr(max_length=255)
    password_hash: constr(max_length=255)
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
    