from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Stock
import logging
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_stock_collection(stock: Stock, db=Depends(get_database)):
    """
    Creating the stock collection in the database.
    """
    try:
        stock_dict = stock.dict(by_alias=True)
        result = await db.stocks.insert_one(stock_dict)
        stock_dict["_id"] = str(result.inserted_id)
        logger.info(f"stock created with ID: {stock_dict['_id']}")
        return stock_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_stock_collection_by_id(stock_id: str, db=Depends(get_database)):
    """
    Getting the stock collection by id from the database.
    """
    try:
        stock = await db.stocks.find_one({"_id": ObjectId(stock_id)})
        if stock:
            return stock
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def update_stock_collection(stock_id: str, stock: Stock, db=Depends(get_database)):
    """
    Updating the stock collection in the database.
    """
    try:
        stock_dict = stock.dict(by_alias=True)
        update_result = await db.stocks.update_one({"_id": ObjectId(stock_id)}, {"$set": stock_dict})
        if update_result.modified_count == 1:
            return stock_dict
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_stock_collection(stock_id: str, db=Depends(get_database)):
    """
    Deleting the stock collection from the database.
    """
    try:
        delete_result = await db.stocks.delete_one({"_id": ObjectId(stock_id)})
        if delete_result.deleted_count == 1:
            return {"status": "success"}
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))