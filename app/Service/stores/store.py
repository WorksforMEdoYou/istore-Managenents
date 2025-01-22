from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.stores.Mysql.mysql_models import StoreDetails as StoreDetailsModel
from app.schemas.stores.StoreDetailsSchema import StoreDetailsCreate, StoreDetails
import logging
from typing import List

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# cheacking wether the store is allready present in the database
def store_validation(store: StoreDetailsCreate, db: Session):
    """
    Store validation
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            StoreDetailsModel.store_name == store.store_name,
            StoreDetailsModel.license_number == store.license_number,
            StoreDetailsModel.gst_number == store.gst_number,
            StoreDetailsModel.gst_state_code == store.gst_state_code,
            StoreDetailsModel.pan == store.pan,
            StoreDetailsModel.address == store.address,
            StoreDetailsModel.email == store.email,
            StoreDetailsModel.mobile == store.mobile,
            StoreDetailsModel.owner_name == store.owner_name,
            StoreDetailsModel.is_main_store == store.is_main_store,
            StoreDetailsModel.latitude == store.latitude,
            StoreDetailsModel.longitude == store.longitude,
            StoreDetailsModel.status == store.status
            ).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
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