from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.store_mysql_models import Substitutes 
from app.schemas.SubstituteSchema import SubstituteCreate, Substitute
import logging
from typing import List
from app.crud.substitutes import create_substitute_record, get_substitute_record, update_substitute_record, delete_substitute_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/substitutes/", response_model=Substitute, status_code=status.HTTP_201_CREATED)
def create_substitute(substitute: SubstituteCreate, db: Session = Depends(get_db)):
    try:
        substitute_medicine = create_substitute_record(substitute, db)
        return substitute_medicine
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/substitutes/", response_model=List[Substitute], status_code=status.HTTP_200_OK)
def list_substitutes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        substitutes = db.query(Substitutes).offset(skip).limit(limit).all()
        return substitutes
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/substitutes/{substitute_id}", response_model=Substitute, status_code=status.HTTP_200_OK)
def get_substitute(substitute_id: int, db: Session = Depends(get_db)):
    try:
        substitute = get_substitute_record(substitute_id, db)
        return substitute
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/substitutes/{substitute_id}", response_model=Substitute, status_code=status.HTTP_200_OK)
def update_substitute(substitute_id: int, substitute: SubstituteCreate, db: Session = Depends(get_db)):
    try:
        db_substitute = update_substitute_record(substitute_id, substitute, db)
        return db_substitute
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/substitutes/{substitute_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_substitute(substitute_id: int, db: Session = Depends(get_db)):
    try:
        db_substitute = delete_substitute_record(substitute_id, db)
        return db_substitute
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))