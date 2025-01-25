from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.store_mysql_models import Category as CategoryModel
from app.schemas.CategorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List
from app.crud.category import creating_category_record, get_category_record, update_category_record, delete_category_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/categories/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        create_category = creating_category_record(category=category, db=db)
        return create_category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/", response_model=List[CategorySchema], status_code=status.HTTP_200_OK)
def list_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        categories = db.query(CategoryModel).offset(skip).limit(limit).all()
        if categories:
            return categories
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = get_category_record(category_id=category_id, db=db)
        return category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/categories/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        db_category = update_category_record(category_id=category_id, category=category, db=db)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/categories/{category_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        db_category = delete_category_record(category_id=category_id, db=db)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))