from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.mysql_session import get_db
from app.models.store_mysql_models import Distributor as DistributorModel
from app.schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate
import logging
from typing import List
from app.crud.distributor import creating_distributor_record, get_all_distributors, get_distibutor_record, update_distributor_record, activate_distributor_record

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

@router.get("/distributors/", status_code=status.HTTP_200_OK)
def list_distributors(db: Session = Depends(get_db)):
    try:
        distributors = get_all_distributors(db=db)
        return distributors
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/distributors/{distributor_name}", response_model=DistributorSchema, status_code=status.HTTP_200_OK)
def get_distributor(distributor_name: str, db: Session = Depends(get_db)):
    try:
        distributor = get_distibutor_record(distributor_name=distributor_name, db=db)
        return distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/distributors/{distributor_name}", response_model=DistributorSchema, status_code=status.HTTP_200_OK)
def update_distributor(distributor_name: str, distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        db_distributor = update_distributor_record(distributor_name=distributor_name, distributor=distributor, db=db)
        return db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/distibutors/active/{distributor_name}", status_code=status.HTTP_200_OK)
def update_distributor_active_status(distributor_name: str, active_flag: int, db: Session = Depends(get_db)):
    try:
        db_distributor = activate_distributor_record(distributor_name=distributor_name, active_flag=active_flag, db=db)
        return db_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
