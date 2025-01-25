from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import Stock
import logging
from app.crud.stock import create_stock_collection, get_stock_collection_by_id, update_stock_collection, delete_stock_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stocks/", response_model=Stock)
async def create_sale_order(stock: Stock, db=Depends(get_database)):
    try:
        stock_dict = await create_stock_collection(stock, db)
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
        stock = await get_stock_collection_by_id(stock_id, db)
        return stock
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stocks/{stock_id}", response_model=Stock)
async def update_stock(stock_id: str, stock: Stock, db=Depends(get_database)):
    try:
        stock_dict = await update_stock_collection(stock_id, stock, db)
        return stock_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/stocks/{stock_id}", response_model=dict)
async def delete_stock(stock_id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_stock_collection(stock_id, db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))