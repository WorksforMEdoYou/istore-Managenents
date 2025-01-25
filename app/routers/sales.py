from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Sale
import logging
from app.crud.sales import create_sale_collection, get_sale_collection_by_id, update_sale_collection, delete_sale_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/sales/", response_model=Sale)
async def create_sale_order(sale: Sale, db=Depends(get_database)):
    try:
        sale_dict = await create_sale_collection(sale, db)
        return sale_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/sales/", response_model=List[Sale])
async def read_sales(db=Depends(get_database)):
    try:
        sales = await db.sales.find().to_list(length=1000)
        for sale in sales:
            sale["_id"] = str(sale["_id"])
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/sales/{sale_id}", response_model=Sale)
async def get_sale_order(sale_id: str, db=Depends(get_database)):
    try:
        sale = await get_sale_collection_by_id(sale_id, db)
        return sale
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/sales/{sale_id}", response_model=Sale)
async def update_sale_order(sale_id: str, sale: Sale, db=Depends(get_database)):
    try:
        sale_dict = await update_sale_collection(sale_id, sale, db)
        return sale_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/sales/{sale_id}", response_model=dict)
async def delete_sale_order(sale_id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_sale_collection(sale_id, db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))