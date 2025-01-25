from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import Distributor as DistributorModel
from app.schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate
import logging
from typing import List

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_distributor_record(distributor, db: Session):
    
    """
    Creating distributor record
    """
    try:
        db_distributor = DistributorModel(**distributor.dict())
        db.add(db_distributor)
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def get_distibutor_record(distributor_id: int, db: Session):
    
    """
    Get distributor record by distributor_id
    """
    try:
        distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if distributor:
            return distributor
        else:
            raise HTTPException(status_code=404, detail="Distributor not found")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def update_distributor_record(distributor_id: int, distributor: DistributorCreate, db: Session):
    
    """
    Update distributor record by distributor_id
    """
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        
        for key, value in distributor.dict().items():
            setattr(db_distributor, key, value)
        
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def delete_distributor_record(distributor_id: int, db: Session):
    
    """
    Delete distributor record by distributor_id
    """
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        
        db.delete(db_distributor)
        db.commit()
        return {"message": "Distributor deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))