from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import parse_obj_as
from app.db.mongodb import get_database
from app.models.MongoDb.Orders import Order
import logging
from bson import ObjectId

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
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
            return order
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: str, order: Order, db=Depends(get_database)):
    try:
        order_dict = order.dict(by_alias=True)
        update_result = await db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": order_dict})
        if update_result.modified_count == 1:
            order_dict["_id"] = str(order_dict["_id"])
            return order_dict
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/orders/{order_id}", response_model=dict)
async def delete_order(order_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.orders.delete_one({"_id": ObjectId(order_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Order deleted successfully"}
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/customer/check")
async def get_user_from_order(db = Depends(get_database)):
    try:
        result = []
        orders_cursor = db.orders.find()
        async for order in orders_cursor:
            customer_id = order["customer_id"]
            customer = await db.customers.find_one({"_id": ObjectId(str(customer_id))})
            if customer:
                customer_name = customer["name"]
                result.append({"customer_id": customer_id, "customer_name": customer_name})
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))