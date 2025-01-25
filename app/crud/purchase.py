from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Purchase
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_purchase_collection(purchase: Purchase, db=Depends(get_database)):
    
    """
    Creating the purchase collection in the database.
    """
    try:
        purchase_dict = purchase.dict(by_alias=True)
        result = await db.purchases.insert_one(purchase_dict)
        purchase_dict["_id"] = str(result.inserted_id)
        logger.info(f"Purchase created with ID: {purchase_dict['_id']}")
        return purchase_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_purchase_collection_by_id(purchase_id: str, db=Depends(get_database)):
    
    """
    Getting the purchase collection by id from the database.
    """
    try:
        purchase = await db.purchases.find_one({"_id": ObjectId(purchase_id)})
        if purchase:
            purchase["_id"] = str(purchase["_id"])
            return purchase
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def update_purchase_collection(purchase_id: str, purchase: Purchase, db=Depends(get_database)):
    
    """
    Updating the purchase collection in the database.
    """
    try:
        purchase_dict = purchase.dict(by_alias=True)
        update_result = await db.purchases.update_one({"_id": ObjectId(purchase_id)}, {"$set": purchase_dict})
        if update_result.modified_count == 1:
            purchase_dict["_id"] = str(purchase_dict["_id"])
            return purchase_dict
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_purchase_collection(purchase_id: str, db=Depends(get_database)):
    
    """
    Deleting the purchase collection from the database.
    """
    try:
        delete_result = await db.purchases.delete_one({"_id": ObjectId(purchase_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Purchase deleted successfully"}
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))