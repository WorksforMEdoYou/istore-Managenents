from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.store_mysql_models import Manufacturer as ManufacturerModel
from app.schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate
import logging
from typing import List

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_manufacturer_record(manufacturer, db: Session):
    
    """
    Creating manufacturer record
    """
    try:
        db_manufacturer = ManufacturerModel(**manufacturer.dict())
        db.add(db_manufacturer)
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error creating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating manufacturer record: " + str(e))

def get_manufacturer_record(manufacturer_id: int, db: Session):
    
    """
    Get manufacturer record by manufacturer_id
    """
    try:
        manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if manufacturer:
            return manufacturer
        else:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
    except Exception as e:
        logger.error(f"Error getting manufacturer record: {e}")
        raise HTTPException(status_code=500, detail="Error getting manufacturer record: " + str(e))

def update_manufacturer_record(manufacturer_id: int, manufacturer: ManufacturerCreate, db: Session):
    
    """
    Update manufacturer record by manufacturer_id
    """
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        
        for key, value in manufacturer.dict().items():
            setattr(db_manufacturer, key, value)
        
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error updating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating manufacturer record: " + str(e))

def delete_manufacturer_record(manufacturer_id: int, db: Session):
    
    """
    Delete manufacturer record by manufacturer_id
    """
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        
        db.delete(db_manufacturer)
        db.commit()
        return {"message": "Manufacturer deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting manufacturer record: " + str(e))
                   