from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    SHOP_KEEPER = "store_keeper" 
    ADMIN = "admin" 
    CUSTOMER = "consumer"

class UserBase(BaseModel):
    username: constr(max_length=255)
    password_hash: constr(max_length=255)
    role: UserRole
    store_id: Optional[int]

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: Optional[int]

    class Config:
        from_attributes = True