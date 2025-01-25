from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import StoreDetails as StoreDetailsModel
from app.schemas.StoreDetailsSchema import StoreDetailsCreate
import logging
from app.db.mysql_session import get_db
from typing import List
from sqlalchemy import or_

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# cheacking wether the store is allready present in the database
def store_validation(store: StoreDetailsCreate, db: Session):
    """
    Store validation by email or mobile
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            or_(
            StoreDetailsModel.email == store.email,
            StoreDetailsModel.mobile == store.mobile
            )).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
# cheacking wether the store is allready present in the database
def store_validation_mobile(mobile:str, db: Session = get_db):
    """
    Store validation by mobile number
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            StoreDetailsModel.mobile == mobile
            ).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    