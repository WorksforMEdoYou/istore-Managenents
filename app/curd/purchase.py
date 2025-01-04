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

@router.get("/purchases/", response_model=List[Purchase])
async def list_purchases(
    distributor_id: Optional[int] = None,
    purchase_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db=Depends(get_database)
):
    try:
        query = {}
        if distributor_id:
            query["distributor_id"] = distributor_id
        if purchase_date:
            query["purchase_date"] = purchase_date
        if start_date and end_date:
            query["purchase_date"] = {"$gte": start_date, "$lte": end_date}
        
        purchases = await db.purchases.find(query).to_list(length=100)
        for purchase in purchases:
            purchase["_id"] = str(purchase["_id"])
        return purchases
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))