from pydantic import BaseModel, constr
from typing import Optional

class SubstituteBase(BaseModel):
    
    """
    Base model for Substitute containing common fields.
    """
    medicine_id: int
    substitute_medicine: constr(max_length=255)

class SubstituteCreate(SubstituteBase):
    
    """
    Pydantic model for creating a new substitute record.    
    """
    pass

class Substitute(SubstituteBase):
    
    """
    Pydantic model for representing detailed substitute information.
    """
    substitute_id: Optional[int]

    class Config:
        from_attributes = True