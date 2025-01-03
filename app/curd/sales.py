from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from ..db.mongodb import get_database
from ..models.mongodb_models import Sale

router = APIRouter()

@router.post("/sales/", response_model=Sale)
async def create_sale_order(sale: Sale, db=Depends(get_database)):
    try:
        sale_dict = sale.dict(by_alias=True)
        result = await db.sales.insert_one(sale_dict)
        sale_dict["_id"] = str(result.inserted_id)
        return sale_dict
    except Exception as e:
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
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/sales/", response_model=List[Sale])
async def list_sale_orders(
    customer_id: Optional[str] = None,
    sale_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db=Depends(get_database)
):
    try:
        query = {}
        if customer_id:
            query["customer_id"] = ObjectId(customer_id)
        if sale_date:
            query["sale_date"] = sale_date
        if start_date and end_date:
            query["sale_date"] = {"$gte": start_date, "$lte": end_date}
        
        sales = await db.sales.find(query).to_list(length=100)
        for sale in sales:
            sale["_id"] = str(sale["_id"])
        return sales
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))