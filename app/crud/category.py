from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.store_mysql_models import Category as CategoryModel
from app.schemas.CategorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List
from datetime import datetime
from app.Service.categoty import check_categoty_available

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_category_record(category:CategoryCreate, db: Session):
    
    """
    Creating category record
    """
    try:
        category_available = check_categoty_available(name = category.category_name, db=db)
        if category_available!="unique":
            raise HTTPException(status_code=400, detail="Category already exists")
        db_category = CategoryModel(
            category_name = category.category_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while creating category record")

def get_category_list(db:Session):
    """
    Get list of all category
    """
    try:
        categorys = db.query(CategoryModel).filter(CategoryModel.active_flag == 1).all()
        category_list = []
        for category in categorys:
            category_data = {
                "category_id": category.category_id,
                "category_name": category.category_name,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "active_flag": category.active_flag
            }
            category_list.append(category_data)
        return category_list
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_category_record(category_name: str, db: Session):
    
    """
    Get category record by category_id    
    """
    try:
        category_available = check_categoty_available(name = category_name, db=db)
        if category_available=="unique":
            raise HTTPException(status_code=400, detail="Category not found")
        category = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if category:
            return category
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while getting category record")
    
def update_category_record(category_name: str, category: CategoryCreate, db: Session):
    
    """
    Update category record by category_id
    """
    try:
        category_available = check_categoty_available(name = category_name, db=db)
        if category_available=="unique":
            raise HTTPException(status_code=404, detail="Category not found")
        db_category = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_category.category_name = category.category_name
        db_category.updated_at = datetime.now()
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while updating category record")

def activate_category_record(category_name, active_flag, db:Session):
    """
    Updating the category active flag 0 or 1
    """
    try:
        category_available = check_categoty_available(name = category_name, db=db)
        if category_available=="unique":
            raise HTTPException(status_code=404, detail="Category not found")
        db_category = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_category.active_flag = active_flag
        db_category.updated_at = datetime.now()
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
