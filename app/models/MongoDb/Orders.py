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