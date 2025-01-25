from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.mysql_session import get_db
from app.models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from app.models.store_mysql_models import Category 
from app.models.store_mysql_models import Manufacturer
from app.schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
from app.utils import validate_by_id
import logging
from datetime import datetime
from app.Service.medicine_master import check_medicine_available
from sqlalchemy.exc import SQLAlchemyError

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_medicine_master_record(medicine_master:MedicineMasterCreate, db: Session):
    
    """
    Creating medicine_master record
    """
    try:
        # Validate category_id
        if not validate_by_id(id=medicine_master.category_id, model=Category, field="category_id"):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not validate_by_id(id=medicine_master.manufacturer_id, model=Manufacturer, field="manufacturer_id"):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        # Validate Medicine name is Available
        validate_medicine_name_available = check_medicine_available(name=medicine_master.medicine_name, db=db)
        if validate_medicine_name_available!="unique":
            raise HTTPException(status_code=400, detail="Medicine already exists")
        
        db_medicine_master = MedicineMasterModel(
            medicine_name = medicine_master.medicine_name,
            generic_name = medicine_master.generic_name,
            hsn_code = medicine_master.hsn_code,
            formulation = medicine_master.formulation,
            strength = medicine_master.strength,
            unit_of_measure = medicine_master.unit_of_measure,
            manufacturer_id = medicine_master.manufacturer_id,
            category_id = medicine_master.category_id,
            activate_medicine = "Active",
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        db.add(db_medicine_master)
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_list(db:Session):
    """
    Get Medicine list by active_flag=1
    """
    try:
        medicines = db.query(MedicineMasterModel).filter(MedicineMasterModel.active_flag == 1).all()
        medicines_list = []
        for medicine in medicines:
            medicine_data = {
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "generic_name": medicine.generic_name,
                "hsn_code": medicine.hsn_code,
                "formulation": medicine.formulation,
                "strength": medicine.strength,
                "unit_of_measure": medicine.unit_of_measure,
                "manufacturer_id": medicine.manufacturer_id,
                "category_id": medicine.category_id,
                "created_at": medicine.created_at,
                "updated_at": medicine.updated_at,
                "active_flag": medicine.active_flag 
            }
            medicines_list.append(medicine_data)
        return medicines_list
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_master_record(medicine_name: str, db: Session):
    
    """
    Get medicine_master record by medicine_id
    """
    try:
        validate_medicine_name_available = check_medicine_available(name=medicine_name, db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine Not found")
        medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if medicine_master:
            return medicine_master
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def update_medicine_master_record(medicine_name: str, medicine_master: MedicineMasterCreate, db: Session):
    
    """
    Update medicine_master record by medicine_id
    """
    try:
        # Validate by medicine_name
        validate_medicine_name_available = check_medicine_available(name=medicine_name, db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        
        # Validate category_id
        if not validate_by_id(id=medicine_master.category_id, model=Category, field="category_id"):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not validate_by_id(id=medicine_master.manufacturer_id, model=Manufacturer, field="manufacturer_id"):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        db_medicine_master.medicine_name = medicine_master.medicine_name,
        db_medicine_master.generic_name = medicine_master.generic_name,
        db_medicine_master.hsn_code = medicine_master.hsn_code,
        db_medicine_master.formulation = medicine_master.formulation,
        db_medicine_master.strength = medicine_master.strength,
        db_medicine_master.unit_of_measure = medicine_master.unit_of_measure,
        db_medicine_master.manufacturer_id = medicine_master.manufacturer_id,
        db_medicine_master.category_id = medicine_master.category_id,
        db_medicine_master.updated_at = datetime.now(),
        
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def activate_medicine_record(medicine_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        validate_medicine_name_available = check_medicine_available(name=medicine_name, db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        db_medicine_master.active_flag = active_flag
        db_medicine_master.updated_at = datetime.now()
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

        