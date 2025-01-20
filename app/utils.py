from fastapi import Depends
from app.db.mongodb import get_database
from app.db.mysql import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# return the data if user exists
def user_already_exists(mysql_db: Session = Depends(get_db), model, user):
    try:
        existing_user = mysql_db.query(model).filter(
            model.username == user.username, 
            model.password == user.password, 
            model.role == user.role
        ).first()
        return existing_user
    except SQLAlchemyError as e:
        # Log the error and re-raise it to handle it at a higher level
        logger.error(f"Database error: {e}")
        raise
    
    