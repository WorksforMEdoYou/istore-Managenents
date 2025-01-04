from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from ..db.mongodb import get_database
from ..models.mongodb_models import Order
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/orders/", response_model=Order)
async def create_order(order: Order, db=Depends(get_database)):
    try:
        order_dict = order.dict(by_alias=True)
        result = await db.orders.insert_one(order_dict)
        order_dict["_id"] = str(result.inserted_id)
        logger.info(f"Order created with ID: {order_dict['_id']}")
        return order_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, db=Depends(get_database)):
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
            return order
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/", response_model=List[Order])
async def list_orders(
    customer_id: Optional[str] = None,
    order_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    order_status: Optional[str] = None,
    db=Depends(get_database)
):
    try:
        query = {}
        if customer_id:
            query["customer_id"] = ObjectId(customer_id)
        if order_date:
            query["order_date"] = order_date
        if start_date and end_date:
            query["order_date"] = {"$gte": start_date, "$lte": end_date}
        if order_status:
            query["order_status"] = order_status
        
        orders = await db.orders.find(query).to_list(length=100)
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))