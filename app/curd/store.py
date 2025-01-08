from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.mysql_schema import StoreDetailsCreate, StoreDetails
import logging
from typing import List

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stores/", response_model=StoreDetails)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = StoreDetailsModel(**store.dict())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/", response_model=List[StoreDetails])
def list_stores(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        stores = db.query(StoreDetailsModel).offset(skip).limit(limit).all()
        return stores
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/{store_id}", response_model=StoreDetails)
def get_store(store_id: int, db: Session = Depends(get_db)):
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if store:
            return store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stores/{store_id}", response_model=StoreDetails)
def update_store(store_id: int, store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        for key, value in store.dict().items():
            setattr(db_store, key, value)
        
        db.commit()
        db.refresh(db_store)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/stores/{store_id}", response_model=dict)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        db.delete(db_store)
        db.commit()
        return {"message": "Store deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))