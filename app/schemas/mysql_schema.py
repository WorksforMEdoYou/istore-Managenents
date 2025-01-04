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

class ManufacturerBase(BaseModel):
    manufacturer_name: constr(max_length=255)

class ManufacturerCreate(ManufacturerBase):
    pass

class Manufacturer(ManufacturerBase):
    manufacturer_id: Optional[int]

    class Config:
        from_attributes = True

class SubstituteBase(BaseModel):
    medicine_id: int
    substitute_medicine: constr(max_length=255)

class SubstituteCreate(SubstituteBase):
    pass

class Substitute(SubstituteBase):
    substitute_id: Optional[int]

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    category_name: constr(max_length=255)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: Optional[int]

    class Config:
        from_attributes = True

class MedicineMasterBase(BaseModel):
    medicine_name: constr(max_length=255)
    generic_name: constr(max_length=255)
    hsn_code: constr(max_length=10)
    formulation: constr(max_length=50)
    strength: constr(max_length=50)
    unit_of_measure: constr(max_length=10)
    manufacturer_id: int
    category_id: int

class MedicineMasterCreate(MedicineMasterBase):
    pass

class MedicineMaster(MedicineMasterBase):
    medicine_id: Optional[int]

    class Config:
        from_attributes = True

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

class DistributorBase(BaseModel):
    distributor_name: constr(max_length=255)

class DistributorCreate(DistributorBase):
    pass

class Distributor(DistributorBase):
    distributor_id: Optional[int]

    class Config:
        from_attributes = True