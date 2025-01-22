from fastapi import Depends, HTTPException, status
from app.db.mongodb import get_database
from app.db.mysql import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from passlib.context import CryptContext
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

# General validation with id and model for MYSQL  
def validate_by_id(id: int, model, field, db: Session = Depends(get_db)):
    try:
        values = db.query(model).filter(model.field == id).first()
        if not values:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="records not found")
        return values
    except SQLAlchemyError as e:
        logger.error(f"Error validating by id: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))

# General validation with id and model for MONGODB
def validate_by_id_mongodb(id: str, model, db = Depends(get_database)):
    try:
        values = db[model].find_one({"_id": ObjectId(str(id))})
        if not values:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="records not found")
        return values
    except Exception as e:
        logger.error(f"Error validating by id: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
