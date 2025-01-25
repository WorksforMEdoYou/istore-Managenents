from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Pricing
import logging
from bson import ObjectId
from app.crud.pricing import create_pricing_collection, get_pricing_collection_by_id, update_pricing_collection, delete_pricing_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/pricing/", response_model=Pricing, status_code=status.HTTP_201_CREATED)
async def create_pricing(pricing: Pricing, db=Depends(get_database)):
    try:
        pricing_dict = await create_pricing_collection(pricing, db)
        return pricing_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/pricing/", response_model=List[Pricing], status_code=status.HTTP_200_OK)
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

@router.get("/pricing/{pricing_id}", response_model=Pricing, status_code=status.HTTP_200_OK)
async def get_pricing(pricing_id: str, db=Depends(get_database)):
    try:
        pricing = await get_pricing_collection_by_id(pricing_id, db)
        return pricing
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/pricing/{pricing_id}", response_model=Pricing, status_code=status.HTTP_200_OK)
async def update_pricing(pricing_id: str, pricing: Pricing, db=Depends(get_database)):
    try:
        pricing_dict = await update_pricing_collection(pricing_id, pricing, db)
        return pricing_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/pricing/{pricing_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_pricing(pricing_id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_pricing_collection(pricing_id, db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))