from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from ..db.mongodb import get_database
from ..models.mongodb_models import Purchase
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/purchases/", response_model=Purchase)
async def create_purchase(purchase: Purchase, db=Depends(get_database)):
    try:
        purchase_dict = purchase.dict(by_alias=True)
        result = await db.purchases.insert_one(purchase_dict)
        purchase_dict["_id"] = str(result.inserted_id)
        logger.info(f"Purchase created with ID: {purchase_dict['_id']}")
        return purchase_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/purchases/", response_model=List[Purchase])
async def get_all_purchases(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        purchases = await db.purchases.find().skip(skip).limit(limit).to_list(length=limit)
        for purchase in purchases:
            purchase["_id"] = str(purchase["_id"])
        return purchases
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/purchases/{purchase_id}", response_model=Purchase)
async def get_purchase(purchase_id: str, db=Depends(get_database)):
    try:
        purchase = await db.purchases.find_one({"_id": ObjectId(purchase_id)})
        if purchase:
            purchase["_id"] = str(purchase["_id"])
            return purchase
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/purchases/{purchase_id}", response_model=Purchase)
async def update_purchase(purchase_id: str, purchase: Purchase, db=Depends(get_database)):
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

@router.delete("/purchases/{purchase_id}", response_model=dict)
async def delete_purchase(purchase_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.purchases.delete_one({"_id": ObjectId(purchase_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Purchase deleted successfully"}
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    