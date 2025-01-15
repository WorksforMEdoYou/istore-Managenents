from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class StoreStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

class StoreDetailsBase(BaseModel):
    store_name: constr(max_length=255)
    license_number: constr(max_length=50)
    gst_state_code: constr(max_length=2)
    gst_number: constr(max_length=50)
    pan: constr(max_length=10)
    address: str
    email: constr(max_length=100)
    mobile: constr(max_length=15)
    owner_name: constr(max_length=255)
    is_main_store: bool
    latitude: float
    longitude: float
    status: StoreStatus  # the store status can be active, inactive or closed

class StoreDetailsCreate(StoreDetailsBase):
    pass

class StoreDetails(StoreDetailsBase):
    store_id: Optional[int]

    class Config:
        from_attributes = True