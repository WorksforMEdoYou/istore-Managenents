from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.stores.Mysql.mysql_models import StoreDetails as StoreDetailsModel
from app.schemas.stores.StoreDetailsSchema import StoreDetailsCreate, StoreDetails
import logging
from typing import List

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_store_record(store: StoreDetailsCreate, db: Session):
    
    """
    Creating store record
    """
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
    
def get_store_record(store_id: int, db: Session):
    """
    Get store record by store_id
    """
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if store:
            return store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def update_store_record(store_id: int, store: StoreDetailsCreate, db: Session):
    """
    Update store record by store_id
    """
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        for key, value in store.dict().items():
            setattr(db_store, key, value)
        
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def delete_store_record(store_id: int, db: Session):
    """
    Delete store record by store_id
    """
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        db.delete(db_store)
        db.commit()
        return {"message": "Store deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))