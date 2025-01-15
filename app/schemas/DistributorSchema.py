from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class DistributorBase(BaseModel):
    distributor_name: constr(max_length=255)

class DistributorCreate(DistributorBase):
    pass

class Distributor(DistributorBase):
    distributor_id: Optional[int]

    class Config:
        from_attributes = True