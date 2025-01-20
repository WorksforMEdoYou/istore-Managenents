from bson import ObjectId
from pydantic import BaseModel, constr, Field

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
 
class Customer(BaseModel):
    
    """
    Base model for the Customer collection.
    """
      
    name: constr(max_length=255) = Field(..., description="Customer Name")
    mobile: constr(max_length=15) = Field(..., description="Customer Mobile")
    email: constr(max_length=255) = Field(..., description="Customer Email")
    password_hash: constr(max_length=255) = Field(..., description="Customer Password Hashed")
    doctor_name: constr(max_length=255) = Field(..., description="Customer Doctor Name")
    class Config:
        arbitrary_types_allowed = True