from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.mysql_session import get_db
from app.models.stores.Mysql.mysql_models import User as UserModel, StoreDetails
from app.schemas.stores.UserSchema import User as UserSchema, UserCreate
from app.utils import get_password_hash
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_user_record(user: UserCreate, db: Session = Depends(get_db)):
    
    """
    create user record
    """
    try:
        hashed_password = get_password_hash(user.password_hash)
        db_user = UserModel(
            username=user.username,
            password_hash=hashed_password,
            role=user.role,
            store_id=user.store_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def get_user_record(user_id: int, db: Session = Depends(get_db)):
    """
    Get user record by user_id
    """
    try:
        user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def update_user_record(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """
    Update user record by user_id
    """
    try:
        db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = get_password_hash(user.password_hash)
        db_user.username = user.username
        db_user.password_hash = hashed_password
        db_user.role = user.role
        db_user.store_id = user.store_id
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def delete_user_record(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user record by user_id
    """
    try:
        db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))