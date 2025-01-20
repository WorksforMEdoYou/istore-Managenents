from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.db.mongodb import get_database
from app.models.MongoDb.Pricing import Pricing
import logging
from bson import ObjectId

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/pricing/", response_model=Pricing)
async def create_pricing(pricing: Pricing, db=Depends(get_database)):
    try:
        pricing_dict = pricing.dict()
        pricing_dict["updated_on"] = datetime.utcnow()
        result = await db.pricing.insert_one(pricing_dict)
        pricing_dict["_id"] = str(result.inserted_id)
        return pricing_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/pricing/", response_model=List[Pricing])
async def list_pricing(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        pricing_cursor = db.pricing.find().skip(skip).limit(limit)
        pricing_list = await pricing_cursor.to_list(length=limit)
        for pricing in pricing_list:
            pricing["_id"] = str(pricing["_id"])
        return pricing_list
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/pricing/{pricing_id}", response_model=Pricing)
async def get_pricing(pricing_id: str, db=Depends(get_database)):
    try:
        pricing = await db.pricing.find_one({"_id": ObjectId(pricing_id)})
        if pricing:
            pricing["_id"] = str(pricing["_id"])
            return pricing
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/pricing/{pricing_id}", response_model=Pricing)
async def update_pricing(pricing_id: str, pricing: Pricing, db=Depends(get_database)):
    try:
        pricing_dict = pricing.dict()
        pricing_dict["updated_on"] = datetime.utcnow()
        update_result = await db.pricing.update_one({"_id": ObjectId(pricing_id)}, {"$set": pricing_dict})
        if update_result.modified_count == 1:
            updated_pricing = await db.pricing.find_one({"_id": ObjectId(pricing_id)})
            updated_pricing["_id"] = str(updated_pricing["_id"])
            return updated_pricing
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/pricing/{pricing_id}", response_model=dict)
async def delete_pricing(pricing_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.pricing.delete_one({"_id": ObjectId(pricing_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Pricing deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))