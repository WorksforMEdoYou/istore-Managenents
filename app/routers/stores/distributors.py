from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.mysql_session import get_db
from app.models.stores.Mysql.mysql_models import Distributor as DistributorModel
from app.schemas.stores.DistributorSchema import Distributor as DistributorSchema, DistributorCreate
import logging
from typing import List
from app.crud.stores.distributor import creating_distributor_record, get_distibutor_record, update_distributor_record, delete_distributor_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/distributors/", response_model=DistributorSchema, status_code=status.HTTP_201_CREATED)
def create_distributor(distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        db_distributor = creating_distributor_record(distributor=distributor, db=db)
        return db_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/distributors/", response_model=List[DistributorSchema], status_code=status.HTTP_200_OK)
def list_distributors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        distributors = db.query(DistributorModel).offset(skip).limit(limit).all()
        return distributors
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/distributors/{distributor_id}", response_model=DistributorSchema, status_code=status.HTTP_200_OK)
def get_distributor(distributor_id: int, db: Session = Depends(get_db)):
    try:
        distributor = get_distibutor_record(distributor_id=distributor_id, db=db)
        return distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/distributors/{distributor_id}", response_model=DistributorSchema, status_code=status.HTTP_200_OK)
def update_distributor(distributor_id: int, distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        db_distributor = update_distributor_record(distributor_id=distributor_id, distributor=distributor, db=db)
        return db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/distributors/{distributor_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_distributor(distributor_id: int, db: Session = Depends(get_db)):
    try:
        db_distributor = delete_distributor_record(distributor_id=distributor_id, db=db)
        return db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))