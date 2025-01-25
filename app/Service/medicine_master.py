from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import MedicineMaster as MedicineMasterModel
from app.schemas.MedicinemasterSchema import MedicineMasterCreate
import logging
from app.db.mysql_session import get_db

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_medicine_available(name:str, db:Session):
    """
    Checking the medicine by name
    """
    try:
        medicine = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == name).first()
        if medicine:
            return medicine
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))