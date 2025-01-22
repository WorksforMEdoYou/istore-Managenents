from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.mysql import get_db
from app.models.stores.Mysql.mysql_models import Substitutes 
from app.models.stores.Mysql.mysql_models import MedicineMaster
from app.schemas.stores.SubstituteSchema import SubstituteCreate, Substitute
import logging
from typing import List
from app.utils import validate_by_id

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_substitute_record(substitute: SubstituteCreate, db: Session):
    
    """
    Create substitute record
    """
    try:
        # Validate medicine_id
        medicine = validate_by_id(id=substitute.medicine_id, model=MedicineMaster, field="medicine_id")
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
    
def get_substitute_record(substitute_id: int, db: Session):
    
    """
    Get substitute record by substitute_id
    """
    try:
        substitute = db.query(Substitutes).filter(Substitutes.substitute_id == substitute_id).first()
        if substitute:
            return substitute
        else:
            raise HTTPException(status_code=404, detail="Substitute not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def update_substitute_record(substitute_id: int, substitute: SubstituteCreate, db: Session):
    
    """
    Update substitute record by substitute_id
    """
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
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def delete_substitute_record(substitute_id: int, db: Session):
    
    """
    Delete substitute record by substitute_id
    """
    try:
        db_substitute = db.query(Substitutes).filter(Substitutes.substitute_id == substitute_id).first()
        if not db_substitute:
            raise HTTPException(status_code=404, detail="Substitute not found")
        
        db.delete(db_substitute)
        db.commit()
        return {"message": "Substitute deleted successfully"}
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))