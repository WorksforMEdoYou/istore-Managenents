from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Sale
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_sale_collection(sale: Sale, db=Depends(get_database)):
    """
    Creating the sale collection in the database.
    """
    try:
        sale_dict = sale.dict(by_alias=True)
        result = await db.sales.insert_one(sale_dict)
        sale_dict["_id"] = str(result.inserted_id)
        logger.info(f"Sale created with ID: {sale_dict['_id']}")
        return sale_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sale_collection_by_id(sale_id: str, db=Depends(get_database)):
    """
    Getting the sale collection by id from the database.
    """
    try:
        sale = await db.sales.find_one({"_id": ObjectId(sale_id)})
        if sale:
            sale["_id"] = str(sale["_id"])
            return sale
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def update_sale_collection(sale_id: str, sale: Sale, db=Depends(get_database)):
    """
    Updating the sale collection in the database.
    """
    try:
        sale_dict = sale.dict(by_alias=True)
        update_result = await db.sales.update_one({"_id": ObjectId(sale_id)}, {"$set": sale_dict})
        if update_result.modified_count == 1:
            sale_dict["_id"] = str(sale_dict["_id"])
            return sale_dict
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_sale_collection(sale_id: str, db=Depends(get_database)):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_result = await db.sales.delete_one({"_id": ObjectId(sale_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Sale order deleted successfully"}
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))