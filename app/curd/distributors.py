from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.mysql_models import Distributor as DistributorModel
from ..schemas.mysql_schema import Distributor as DistributorSchema, DistributorCreate
import logging
from typing import List

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/distributors/", response_model=DistributorSchema)
def create_distributor(distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        db_distributor = DistributorModel(**distributor.dict())
        db.add(db_distributor)
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/distributors/", response_model=List[DistributorSchema])
def list_distributors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        distributors = db.query(DistributorModel).offset(skip).limit(limit).all()
        return distributors
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/distributors/{distributor_id}", response_model=DistributorSchema)
def get_distributor(distributor_id: int, db: Session = Depends(get_db)):
    try:
        distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if distributor:
            return distributor
        else:
            raise HTTPException(status_code=404, detail="Distributor not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/distributors/{distributor_id}", response_model=DistributorSchema)
def update_distributor(distributor_id: int, distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        
        for key, value in distributor.dict().items():
            setattr(db_distributor, key, value)
        
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/distributors/{distributor_id}", response_model=dict)
def delete_distributor(distributor_id: int, db: Session = Depends(get_db)):
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_id == distributor_id).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        
        db.delete(db_distributor)
        db.commit()
        return {"message": "Distributor deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))