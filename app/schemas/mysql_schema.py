from pydantic import BaseModel
from typing import Optional

class StoreDetailsBase(BaseModel):
    store_name: str
    license_number: str
    gst_state_code: str
    gst_number: str
    pan: str
    address: str
    email: str
    mobile: str
    owner_name: str
    is_main_store: bool
    latitude: float
    longitude: float
    status: str  # Corrected annotation

class StoreDetailsCreate(StoreDetailsBase):
    pass

class StoreDetails(StoreDetailsBase):
    store_id: Optional[int]

    class Config:
        from_attributes = True

class ManufacturerBase(BaseModel):
    manufacturer_name: str

class ManufacturerCreate(ManufacturerBase):
    pass

class Manufacturer(ManufacturerBase):
    manufacturer_id: Optional[int]

    class Config:
        from_attributes = True

class SubstituteBase(BaseModel):
    medicine_id: int
    substitute_medicine: str

class SubstituteCreate(SubstituteBase):
    pass

class Substitute(SubstituteBase):
    substitute_id: Optional[int]

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: Optional[int]

    class Config:
        from_attributes = True

class MedicineMasterBase(BaseModel):
    medicine_name: str
    generic_name: str
    hsn_code: str
    formulation: str
    strength: str
    unit_of_measure: str
    manufacturer_id: int
    category_id: int

class MedicineMasterCreate(MedicineMasterBase):
    pass

class MedicineMaster(MedicineMasterBase):
    medicine_id: Optional[int]

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    password_hash: str
    role: str
    store_id: Optional[int]

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: Optional[int]

    class Config:
        from_attributes = True

class DistributorBase(BaseModel):
    distributor_name: str

class DistributorCreate(DistributorBase):
    pass

class Distributor(DistributorBase):
    distributor_id: Optional[int]

    class Config:
        from_attributes = True