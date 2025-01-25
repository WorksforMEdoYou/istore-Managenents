from fastapi import Depends, HTTPException
from typing import List
from datetime import datetime
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Pricing
import logging
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_pricing_collection(pricing: Pricing, db=Depends(get_database)):
    
    """
    Creating the pricing collection in the database.
    """
    try:
        pricing_dict = pricing.dict()
        pricing_dict["updated_on"] = datetime.utcnow()
        result = await db.pricing.insert_one(pricing_dict)
        pricing_dict["_id"] = str(result.inserted_id)
        return pricing_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_pricing_collection_by_id(pricing_id: str, db=Depends(get_database)):
    
    """
    Getting the pricing collection by ID from the database.
    """
    try:
        pricing = await db.pricing.find_one({"_id": ObjectId(str(pricing_id))})
        if pricing:
            pricing["_id"] = str(pricing["_id"])
            return pricing
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def update_pricing_collection(pricing_id: str, pricing: Pricing, db=Depends(get_database)):
    
    """
    Upgating the pricing collection in the database.
    """
    try:
        pricing_dict = pricing.dict()
        pricing_dict["updated_on"] = datetime.utcnow()
        update_result = await db.pricing.update_one({"_id": ObjectId(str(pricing_id))}, {"$set": pricing_dict})
        if update_result.modified_count == 1:
            updated_pricing = await db.pricing.find_one({"_id": ObjectId(str(pricing_id))})
            updated_pricing["_id"] = str(updated_pricing["_id"])
            return updated_pricing
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def delete_pricing_collection(pricing_id: str, db=Depends(get_database)):
    
    """
    Deleting the pricing collection in the database.
    """
    try:
        delete_result = await db.pricing.delete_one({"_id": ObjectId(str(pricing_id))})
        if delete_result.deleted_count == 1:
            return {"message": "Pricing deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))