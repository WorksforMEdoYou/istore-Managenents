from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import Distributor as DistributorModel
from app.schemas.DistributorSchema import DistributorCreate
import logging
from app.db.mysql_session import get_db

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_distributor_available(name:str, db:Session):
    """
    Check distributor by name
    """
    try:
        distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == name).first()
        if distributor:
            return distributor
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))