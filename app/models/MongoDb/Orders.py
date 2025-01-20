from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List
from datetime import datetime
from app.models.MongoDb.Eunums import OrderStatus, PaymentMethod

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
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine master table")
    quantity: int = Field(..., description="Quantity of the ordered medicine")
    price: float = Field(..., description="Price of the ordered medicine")
    unit: constr(max_length=255) = Field(..., description="unit of the ordered medicine")
    class Config:
        arbitrary_types_allowed = True

class Order(BaseModel):
    
    """
    Base model for the Order collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    customer_id: str = Field(..., description="Customer ObjectID from the Customer Collection") # from customer id
    order_date: datetime = Field(..., description="Order Date")
    order_status: OrderStatus = Field(..., description="Order Status can be pending, processing, shipped, delivered, cancelled ")  # "pending", "processing", "shipped", "delivered", "cancelled"
    payment_method: PaymentMethod = Field(..., description="Payment Method can be Online, Cash, Cash on delivery")  # "online", "cash", "cod"
    total_amount: float = Field(..., description="Total amount of the ordered items")
    order_items: List[OrderItem] = Field(..., description="Order_items List of items ")
    class Config:
        arbitrary_types_allowed = True