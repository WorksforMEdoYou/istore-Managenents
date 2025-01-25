from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import parse_obj_as
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Order
import logging
from app.crud.orders import create_order_collection, get_order_collection, update_order_collection, delete_order_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/orders/", response_model=Order)
async def create_order(order: Order, db=Depends(get_database)):
    try:
        order_dict = await create_order_collection(order=order, db=db)
        return order_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/", response_model=List[Order])
async def get_all_orders(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        orders = await db.orders.find().skip(skip).limit(limit).to_list(length=limit)
        return parse_obj_as(List[Order], orders)
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, db=Depends(get_database)):
    try:
        order = await get_order_collection(order_id=order_id, db=db)
        return order
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: str, order: Order, db=Depends(get_database)):
    try:
        order_dict = await update_order_collection(order_id=order_id, order=order, db=db)
        return order_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/orders/{order_id}", response_model=dict)
async def delete_order(order_id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_order_collection(order_id=order_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))