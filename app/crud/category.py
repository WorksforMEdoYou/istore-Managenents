from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.store_mysql_models import Category as CategoryModel
from app.schemas.CategorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_category_record(category, db: Session):
    
    """
    Creating category record
    """
    try:
        db_category = CategoryModel(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while creating category record")
    
def get_category_record(category_id: int, db: Session):
    
    """
    Get category record by category_id    
    """
    try:
        category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
        if category:
            return category
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while getting category record")
    
def update_category_record(category_id: int, category: CategoryCreate, db: Session):
    
    """
    Update category record by category_id
    """
    try:
        db_category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        for key, value in category.dict().items():
            setattr(db_category, key, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while updating category record")
    
def delete_category_record(category_id: int, db: Session):
    
    """
    Delete category record by category_id
    """
    try:
        db_category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        db.delete(db_category)
        db.commit()
        return {"message": "Category deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while deleting category record")