from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Customer
import logging
from app.crud.customer import create_customer_collection, get_customer_collection, update_customer_collection, delete_customer_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/customers/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: Customer, db=Depends(get_database)):
    try:
        customer_dict = await create_customer_collection(customer=customer, db=db)
        return customer_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/customers/", response_model=List[Customer], status_code=status.HTTP_200_OK)
async def list_customers(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        customers = await db.customers.find().skip(skip).limit(limit).to_list(length=limit)
        if customers:
            return customers
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def get_customer(customer_id: str, db=Depends(get_database)):
    try:
        customer = await get_customer_collection(customer_id=customer_id, db=db)
        return customer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
async def update_customer(customer_id: str, customer: Customer, db=Depends(get_database)):
    try:
        updated_customer = await update_customer_collection(customer_id=customer_id, customer=customer, db=db)
        return updated_customer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/customers/{customer_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_customer(customer_id: str, db=Depends(get_database)):
    try:
        deleted_customer = await delete_customer_collection(customer_id=customer_id, db=db)
        return deleted_customer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))