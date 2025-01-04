from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.mysql_models import Manufacturer as ManufacturerModel
from ..schemas.mysql_schema import ManufacturerCreate, Manufacturer
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/manufacturers/", response_model=Manufacturer)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = ManufacturerModel(**manufacturer.dict())
        db.add(db_manufacturer)
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/{manufacturer_id}", response_model=Manufacturer)
def get_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        return db_manufacturer
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/", response_model=list[Manufacturer])
def list_manufacturers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return db.query(ManufacturerModel).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/manufacturers/{manufacturer_id}", response_model=Manufacturer)
def modify_manufacturer(manufacturer_id: int, manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == manufacturer_id).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        
        for key, value in manufacturer.dict().items():
            setattr(db_manufacturer, key, value)
        
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))