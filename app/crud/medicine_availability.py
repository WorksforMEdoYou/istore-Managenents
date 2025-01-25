from fastapi import Depends, HTTPException
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import MedicineAvailability
import logging
from bson import ObjectId

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_medicine_availability_collection(medicine_availability: MedicineAvailability, db=Depends(get_database)):
    
    """
    Creating medicine availability collection
    """
    try:
        medicine_availability_dict = medicine_availability.dict()
        result = await db.medicine_availability.insert_one(medicine_availability_dict)
        medicine_availability_dict["_id"] = str(result.inserted_id)
        logger.info(f"Medicine availability created with ID: {medicine_availability_dict['_id']}")
        return medicine_availability_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_medicine_availability_collection(medicine_availability_id: str, db=Depends(get_database)):
    """
    Get medicine availability collection by medicine_availability_id
    """
    try:
        medicine_availability = await db.medicine_availability.find_one({"_id": ObjectId(id)})
        if medicine_availability:
            medicine_availability["_id"] = str(medicine_availability["_id"])
            return medicine_availability
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def update_medicine_availability_collection(medicine_availability_id: str, medicine_availability: MedicineAvailability, db=Depends(get_database)):
    """
    Update medicine availability collection by medicine_availability_id
    """
    try:
        update_result = await db.medicine_availability.update_one({"_id": ObjectId(id)}, {"$set": medicine_availability.dict()})
        if update_result.modified_count == 1:
            updated_medicine_availability = await db.medicine_availability.find_one({"_id": ObjectId(id)})
            if updated_medicine_availability:
                updated_medicine_availability["_id"] = str(updated_medicine_availability["_id"])
                return updated_medicine_availability
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_medicine_availability_collection(medicine_availability_id: str, db=Depends(get_database)):
    """
    Delete medicine availability collection by medicine_availability_id
    """
    try:
        delete_result = await db.medicine_availability.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            return {"message": "Medicine availability deleted successfully"}
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))