from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.mysql_models import Substitutes
from ..schemas.mysql_schema import SubstituteCreate, Substitute

router = APIRouter()

@router.get("/substitutes/", response_model=list[Substitute])
def list_substitutes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        substitutes = db.query(Substitutes).offset(skip).limit(limit).all()
        return substitutes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.post("/substitutes/", response_model=Substitute)
def create_substitute(substitute: SubstituteCreate, db: Session = Depends(get_db)):
    try:
        db_substitute = Substitutes(**substitute.dict())
        db.add(db_substitute)
        db.commit()
        db.refresh(db_substitute)
        return db_substitute
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))