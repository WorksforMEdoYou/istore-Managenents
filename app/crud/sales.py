from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.MongoDb.Sale import Sale
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/sales/", response_model=Sale)
async def create_sale_order(sale: Sale, db=Depends(get_database)):
    try:
        sale_dict = sale.dict(by_alias=True)
        result = await db.sales.insert_one(sale_dict)
        sale_dict["_id"] = str(result.inserted_id)
        logger.info(f"Sale created with ID: {sale_dict['_id']}")
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
        sale = await db.sales.find_one({"_id": ObjectId(sale_id)})
        if sale:
            sale["_id"] = str(sale["_id"])
            return sale
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/sales/{sale_id}", response_model=Sale)
async def update_sale_order(sale_id: str, sale: Sale, db=Depends(get_database)):
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

@router.delete("/sales/{sale_id}", response_model=dict)
async def delete_sale_order(sale_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.sales.delete_one({"_id": ObjectId(sale_id)})
        if delete_result.deleted_count == 1:
            return {"message": "Sale order deleted successfully"}
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))