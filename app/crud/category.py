from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.Mysql.Category import Category as CategoryModel
from app.schemas.CategorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/categories/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        db_category = CategoryModel(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/", response_model=List[CategorySchema])
def list_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        categories = db.query(CategoryModel).offset(skip).limit(limit).all()
        return categories
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
        if category:
            return category
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/categories/{category_id}", response_model=CategorySchema)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail="Database error: " + str(e))