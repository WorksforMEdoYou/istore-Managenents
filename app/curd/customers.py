from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.mongodb import get_database
from ..models.mongodb_models import Customer
import logging
from bson import ObjectId
from ..utils.utils import str_objectId

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/customers/", response_model=Customer)
async def create_customer(customer: Customer, db=Depends(get_database)):
    """ try:
        customer_id = await db.customers.insert_one(customer.dict())
        customer = await db.customers.find_one({"_id": customer_id.inserted_id})
        return customer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)) """
    try:
        customer_dict = customer.dict()
        customer_id = await db.customers.insert_one(customer_dict)
        customer_dict["_id"] = str_objectId(customer_id.inserted_id)
        return customer_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
@router.get("/customers/", response_model=List[Customer])
async def list_customers(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        list=[]
        customers = await db.customers.find().skip(skip).limit(limit).to_list(length=limit)
        for customer in customers:
            a = {
                "id": customer["_id"],
                "name": customer["name"],
                "mobile": customer["mobile"],
                "email": customer["email"],
                "password_hash": customer["password_hash"],
                "doctor_name": customer["doctor_name"]
            }
            print(a)
            list.append(a)
        return list
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, db=Depends(get_database)):
    try:
        customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer: Customer, db=Depends(get_database)):
    try:
        update_result = await db.customers.update_one({"_id": ObjectId(customer_id)}, {"$set": customer.dict()})
        if update_result.modified_count == 1:
            updated_customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/customers/{customer_id}", response_model=dict)
async def delete_customer(customer_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.customers.delete_one({"_id": ObjectId(customer_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))