from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.mongodb_models import Stock, SaleItem
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stocks/", response_model=Stock)
async def create_sale_order(stock: Stock, db=Depends(get_database)):
    try:
        stock_dict = stock.dict(by_alias=True)
        result = await db.stocks.insert_one(stock_dict)
        stock_dict["_id"] = str(result.inserted_id)
        logger.info(f"stock created with ID: {stock_dict['_id']}")
        return stock_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/", response_model=List[Stock])
async def read_stocks(db=Depends(get_database)):
    try:
        stocks = await db.stocks.find().to_list(length=None)
        return stocks
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/{stock_id}", response_model=Stock)
async def read_stock(stock_id: str, db=Depends(get_database)):
    try:
        stock = await db.stocks.find_one({"_id": ObjectId(stock_id)})
        if stock:
            return stock
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stocks/{stock_id}", response_model=Stock)
async def update_stock(stock_id: str, stock: Stock, db=Depends(get_database)):
    try:
        stock_dict = stock.dict(by_alias=True)
        update_result = await db.stocks.update_one({"_id": ObjectId(stock_id)}, {"$set": stock_dict})
        if update_result.modified_count == 1:
            return stock_dict
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/stocks/{stock_id}", response_model=dict)
async def delete_stock(stock_id: str, db=Depends(get_database)):
    try:
        delete_result = await db.stocks.delete_one({"_id": ObjectId(stock_id)})
        if delete_result.deleted_count == 1:
            return {"status": "success"}
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))