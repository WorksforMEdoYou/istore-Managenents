from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.Mysql.Manufacturer import Manufacturer as ManufacturerModel
from app.schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate
import logging
from typing import List

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/manufacturers/", response_model=ManufacturerSchema)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = ManufacturerModel(**manufacturer.dict())
        db.add(db_manufacturer)
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/", response_model=List[ManufacturerSchema])
def list_manufacturers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        manufacturers = db.query(ManufacturerModel).offset(skip).limit(limit).all()
        return manufacturers
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/{manufacturer_id}", response_model=ManufacturerSchema)
def get_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    try:
        manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if manufacturer:
            return manufacturer
        else:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/manufacturers/{manufacturer_id}", response_model=ManufacturerSchema)
def update_manufacturer(manufacturer_id: int, manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
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
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/manufacturers/{manufacturer_id}", response_model=dict)
def delete_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        
        db.delete(db_manufacturer)
        db.commit()
        return {"message": "Manufacturer deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))