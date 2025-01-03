from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.mysql_schema import StoreDetailsCreate, StoreDetails

router = APIRouter()

@router.post("/stores/", response_model=StoreDetails)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = StoreDetailsModel(**store.dict())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stores/{store_id}", response_model=StoreDetails)
def modify_store(store_id: int, store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        for key, value in store.dict().items():
            setattr(db_store, key, value)
        
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/{store_id}", response_model=StoreDetails)
def get_store(store_id: int, db: Session = Depends(get_db)):
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        return db_store
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/", response_model=list[StoreDetails])
def list_stores(storename: Optional[str] = None, location: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(StoreDetailsModel)
        if storename:
            query = query.filter(StoreDetailsModel.store_name == storename)
        if location:
            query = query.filter(StoreDetailsModel.address == location)
        if status:
            query = query.filter(StoreDetailsModel.status == status)
        return query.all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))