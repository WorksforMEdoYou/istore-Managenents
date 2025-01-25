from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import Manufacturer as ManufacturerModel
from app.schemas.ManufacturerSchema import ManufacturerCreate
import logging

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_manufacturer_available(name: str, db: Session):
    """
    Check manufacturer by name
    """
    try:
        manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == name).first()
        if manufacturer:
            return manufacturer
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))