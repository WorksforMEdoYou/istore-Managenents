from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.mysql_session import get_db
from app.models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from app.models.store_mysql_models import Category 
from app.models.store_mysql_models import Manufacturer
from app.schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
from app.utils import validate_by_id
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_medicine_master_record(medicine_master, db: Session):
    
    """
    Creating medicine_master record
    """
    try:
        # Validate category_id
        if not validate_by_id(id=medicine_master.category_id, model=Category, field="category_id"):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not validate_by_id(id=medicine_master.manufacturer_id, model=Manufacturer, field="manufacturer_id"):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        db_medicine_master = MedicineMasterModel(**medicine_master.dict())
        db.add(db_medicine_master)
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_master_record(medicine_id: int, db: Session):
    
    """
    Get medicine_master record by medicine_id
    """
    try:
        medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if medicine_master:
            return medicine_master
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def update_medicine_master_record(medicine_id: int, medicine_master: MedicineMasterCreate, db: Session):
    
    """
    Update medicine_master record by medicine_id
    """
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        for key, value in medicine_master.dict().items():
            setattr(db_medicine_master, key, value)
        
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def delete_medicine_master_record(medicine_id: int, db: Session):
    
    """
    Delete medicine_master record by medicine_id
    """
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        db.delete(db_medicine_master)
        db.commit()
        return {"message": "Medicine deleted successfully"}
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
        