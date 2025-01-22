from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.mongodb import get_database
from app.models.stores.MongoDb.mongodb_models import Purchase
import logging
from app.crud.stores.purchase import create_purchase_collection, get_purchase_collection_by_id, update_purchase_collection, delete_purchase_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/purchases/", response_model=Purchase)
async def create_purchase(purchase: Purchase, db=Depends(get_database)):
    try:
        purchase_dict = await create_purchase_collection(purchase, db)
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
        purchase = await get_purchase_collection_by_id(purchase_id, db)
        return purchase
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/purchases/{purchase_id}", response_model=Purchase)
async def update_purchase(purchase_id: str, purchase: Purchase, db=Depends(get_database)):
    try:
        purchase_dict = await update_purchase_collection(purchase_id, purchase, db)
        return purchase_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/purchases/{purchase_id}", response_model=dict)
async def delete_purchase(purchase_id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_purchase_collection(purchase_id, db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))