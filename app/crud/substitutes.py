from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.mysql import get_db
from app.models.Mysql.Substitute import Substitutes 
from app.models.Mysql.Medicinemaster import MedicineMaster
from app.schemas.mysql_schema import SubstituteCreate, Substitute
import logging
from typing import List

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/substitutes/", response_model=Substitute)
def create_substitute(substitute: SubstituteCreate, db: Session = Depends(get_db)):
    try:
        # Validate medicine_id
        medicine = db.query(MedicineMaster).filter(MedicineMaster.medicine_id == substitute.medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=400, detail="Invalid medicine_id")

        db_substitute = Substitutes(**substitute.dict())
        db.add(db_substitute)
        db.commit()
        db.refresh(db_substitute)
        return db_substitute
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/substitutes/", response_model=List[Substitute])
def list_substitutes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        substitutes = db.query(Substitutes).offset(skip).limit(limit).all()
        return substitutes
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/substitutes/{substitute_id}", response_model=Substitute)
def get_substitute(substitute_id: int, db: Session = Depends(get_db)):
    try:
        substitute = db.query(Substitutes).filter(Substitutes.substitute_id == substitute_id).first()
        if substitute:
            return substitute
        else:
            raise HTTPException(status_code=404, detail="Substitute not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/substitutes/{substitute_id}", response_model=Substitute)
def update_substitute(substitute_id: int, substitute: SubstituteCreate, db: Session = Depends(get_db)):
    try:
        db_substitute = db.query(Substitutes).filter(Substitutes.substitute_id == substitute_id).first()
        if not db_substitute:
            raise HTTPException(status_code=404, detail="Substitute not found")
        
        for key, value in substitute.dict().items():
            setattr(db_substitute, key, value)
        
        db.commit()
        db.refresh(db_substitute)
        return db_substitute
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/substitutes/{substitute_id}", response_model=dict)
def delete_substitute(substitute_id: int, db: Session = Depends(get_db)):
    try:
        db_substitute = db.query(Substitutes).filter(Substitutes.substitute_id == substitute_id).first()
        if not db_substitute:
            raise HTTPException(status_code=404, detail="Substitute not found")
        
        db.delete(db_substitute)
        db.commit()
        return {"message": "Substitute deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))