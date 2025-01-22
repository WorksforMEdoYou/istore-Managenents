from fastapi import Depends, HTTPException
from typing import List
from app.db.mongodb import get_database
from app.models.stores.MongoDb.mongodb_models import Customer
import logging
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_customer_collection(customer: Customer, db=Depends(get_database)):
    
    """
    Creating customer collection
    """
    try:
        customer_dict = customer.dict()
        customer_id = await db.customers.insert_one(customer_dict)
        customer_dict["_id"] = str(customer_id.inserted_id)
        return customer_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_customer_collection(customer_id: str, db=Depends(get_database)):
    """
    Get customer collection by customer_id
    """
    try:
        customer = await db.customers.find_one({"_id": ObjectId(str(customer_id))})
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        
async def update_customer_collection(customer_id: str, customer: Customer, db=Depends(get_database)):
    """
    Update customer collection by customer_id
    """
    try:
        update_result = await db.customers.update_one({"_id": ObjectId(str(customer_id))}, {"$set": customer.dict()})
        if update_result.modified_count == 1:
            updated_customer = await db.customers.find_one({"_id": ObjectId(str(customer_id))})
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_customer_collection(customer_id: str, db=Depends(get_database)):
    """
    Delete customer collection by customer_id
    """
    try:
        delete_result = await db.customers.delete_one({"_id": ObjectId(str(customer_id))})
        if delete_result.deleted_count == 1:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))