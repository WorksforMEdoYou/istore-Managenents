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

@router.get("/stocks/", response_model=List[Stock])
async def list_stocks(db=Depends(get_database)):
    try:
        stocks = await db.stocks.find().to_list(length=100)
        for stock in stocks:
            stock["_id"] = str(stock["_id"])
        return stocks
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/{medicine_id}", response_model=Stock)
async def get_stocks_by_medicine(medicine_id: int, db=Depends(get_database)):
    try:
        stock = await db.stocks.find_one({"medicine_id": medicine_id})
        if stock:
            stock["_id"] = str(stock["_id"])
            return stock
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/medicines/{medicine_id}", response_model=Stock)
async def get_medicine(medicine_id: int, db=Depends(get_database)):
    try:
        medicine = await db.stocks.find_one({"medicine_id": medicine_id})
        if medicine:
            medicine["_id"] = str(medicine["_id"])
            return medicine
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/batches/", response_model=List[SaleItem])
async def list_batches(db=Depends(get_database)):
    try:
        batches = await db.stocks.aggregate([
            {"$unwind": "$batches"},
            {"$replaceRoot": {"newRoot": "$batches"}}
        ]).to_list(length=100)
        for batch in batches:
            batch["_id"] = str(batch["_id"])
        return batches
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/batches/{batch_id}", response_model=SaleItem)
async def get_batch(batch_id: str, db=Depends(get_database)):
    try:
        batch = await db.stocks.aggregate([
            {"$unwind": "$batches"},
            {"$match": {"batches._id": ObjectId(batch_id)}},
            {"$replaceRoot": {"newRoot": "$batches"}}
        ]).to_list(length=1)
        if batch:
            batch[0]["_id"] = str(batch[0]["_id"])
            return batch[0]
        raise HTTPException(status_code=404, detail="Batch not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

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