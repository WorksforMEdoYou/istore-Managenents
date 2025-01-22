from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import parse_obj_as
from app.db.mongodb import get_database
from app.models.stores.MongoDb.mongodb_models import Order
import logging
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_order_collection(order: Order, db=Depends(get_database)):
    """
    Create a new order in the database.
    """
    try:
        order_dict = order.dict(by_alias=True)
        result = await db.orders.insert_one(order_dict)
        order_dict["_id"] = str(result.inserted_id)
        logger.info(f"Order created with ID: {order_dict['_id']}")
        return order_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_order_collection(order_id: str, db=Depends(get_database)):
    """
    Get a specific order from the database.
    """
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
            return order
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def update_order_collection(order_id: str, order: Order, db=Depends(get_database)):
    """
    Update a specific order in the database.
    """
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

async def delete_order_collection(order_id: str, db=Depends(get_database)):
    """
    Delete a specific order from the database.
    """
    try:
        delete_result = await db.orders.delete_one({"_id": ObjectId(order_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Order deleted successfully"}
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))