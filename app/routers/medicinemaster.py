from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.mysql_session import get_db
from app.models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from app.schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
import logging
from app.crud.medicine_master import create_medicine_master_record, get_medicine_master_record, update_medicine_master_record, delete_medicine_master_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_master/", response_model=MedicineMasterSchema, status_code=status.HTTP_201_CREATED)
def create_medicine_master(medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        db_medicine_master = create_medicine_master_record(medicine_master=medicine_master, db=db)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/", response_model=List[MedicineMasterSchema], status_code=status.HTTP_200_OK)
def get_all_medicine_master(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        medicine_master = db.query(MedicineMasterModel).offset(skip).limit(limit).all()
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/{medicine_id}", response_model=MedicineMasterSchema, status_code=status.HTTP_200_OK)
def get_medicine_master(medicine_id: int, db: Session = Depends(get_db)):
    try:
        medicine_master = get_medicine_master_record(medicine_id=medicine_id, db=db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_master/{medicine_id}", response_model=MedicineMasterSchema, status_code=status.HTTP_200_OK)
def update_medicine_master(medicine_id: int, medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        db_medicine_master = update_medicine_master_record(medicine_id=medicine_id, medicine_master=medicine_master, db=db)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/medicine_master/{medicine_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_medicine_master(medicine_id: int, db: Session = Depends(get_db)):
    try:
        db_medicine_master = delete_medicine_master_record(medicine_id=medicine_id, db=db)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))