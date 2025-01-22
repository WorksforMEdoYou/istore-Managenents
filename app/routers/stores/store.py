from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.mysql_session import get_db
from app.models.stores.Mysql.mysql_models import StoreDetails as StoreDetailsModel
from app.schemas.stores.StoreDetailsSchema import StoreDetailsCreate, StoreDetails
import logging
from typing import List
from app.crud.stores.store import create_store_record, get_store_record, update_store_record, delete_store_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stores/", response_model=StoreDetails, status_code=status.HTTP_201_CREATED)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = create_store_record(store, db)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/", response_model=List[StoreDetails], status_code=status.HTTP_200_OK)
def list_stores(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        stores = db.query(StoreDetailsModel).offset(skip).limit(limit).all()
        return stores
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/{store_id}", response_model=StoreDetails, status_code=status.HTTP_200_OK)
def get_store(store_id: int, db: Session = Depends(get_db)):
    try:
        store = get_store_record(store_id, db)
        return store
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stores/{store_id}", response_model=StoreDetails, status_code=status.HTTP_200_OK)
def update_store(store_id: int, store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = update_store_record(store_id, store, db)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/stores/{store_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    try:
        db_store = delete_store_record(store_id, db)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))