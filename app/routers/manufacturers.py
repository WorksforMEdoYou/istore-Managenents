from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.store_mysql_models import Manufacturer as ManufacturerModel
from app.schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate
import logging
from typing import List
from app.crud.manufacturers import create_manufacturer_record, get_manufacturer_record, update_manufacturer_record, get_manufacturer_list, activate_manufacturer_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/manufacturers/", response_model=ManufacturerSchema, status_code=status.HTTP_201_CREATED)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = create_manufacturer_record(manufacturer=manufacturer, db=db)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/", status_code=status.HTTP_200_OK)
def list_manufacturers(db: Session = Depends(get_db)):
    try:
        manufacturers = get_manufacturer_list(db=db)
        return manufacturers
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/{manufacturer_name}", status_code=status.HTTP_200_OK)
def get_manufacturer(manufacturer_name: str, db: Session = Depends(get_db)):
    try:
        manufacturer = get_manufacturer_record(manufacturer_name=manufacturer_name, db=db)
        return manufacturer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/manufacturers/{manufacturer_name}", response_model=ManufacturerSchema, status_code=status.HTTP_200_OK)
def update_manufacturer(manufacturer_name: str, manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = update_manufacturer_record(manufacturer_name=manufacturer_name, manufacturer=manufacturer, db=db)
        return db_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/manufacturers/activate/{manufacturer_name}", status_code=status.HTTP_200_OK)
def activate_deactivate(manufacturer_name:str, active_flag:int, db:Session = Depends(get_db)):
    try:
        db_manufacturer = activate_manufacturer_record(manufacturer_name=manufacturer_name, active_flag=active_flag, db=db)
        return db_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
