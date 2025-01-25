from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.store_mysql_models import Category as CategotyModel
from app.schemas.CategorySchema import CategoryCreate
import logging
from app.db.mysql_session import get_db

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_categoty_available(name:str, db:Session = get_db):
    """
    Checking the category by name
    """
    try:
        categoty = db.query(CategotyModel).filter(CategotyModel.category_name == name).first()
        if categoty:
            return categoty
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))