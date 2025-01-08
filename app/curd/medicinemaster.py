from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.mysql_models import MedicineMaster as MedicineMasterModel, Category, Manufacturer
from ..schemas.mysql_schema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_master/", response_model=MedicineMasterSchema)
def create_medicine_master(medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        # Validate category_id
        category = db.query(Category).filter(Category.category_id == medicine_master.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == medicine_master.manufacturer_id).first()
        if not manufacturer:
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")

        db_medicine_master = MedicineMasterModel(**medicine_master.dict())
        db.add(db_medicine_master)
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/", response_model=List[MedicineMasterSchema])
def get_all_medicine_master(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        medicine_master = db.query(MedicineMasterModel).offset(skip).limit(limit).all()
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/{medicine_id}", response_model=MedicineMasterSchema)
def get_medicine_master(medicine_id: int, db: Session = Depends(get_db)):
    try:
        medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if medicine_master:
            return medicine_master
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_master/{medicine_id}", response_model=MedicineMasterSchema)
def update_medicine_master(medicine_id: int, medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        for key, value in medicine_master.dict().items():
            setattr(db_medicine_master, key, value)
        
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/medicine_master/{medicine_id}", response_model=dict)
def delete_medicine_master(medicine_id: int, db: Session = Depends(get_db)):
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        db.delete(db_medicine_master)
        db.commit()
        return {"message": "Medicine deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))