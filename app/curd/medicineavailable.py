from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.mongodb import get_database
from ..models.mongodb_models import MedicineAvailability, PyObjectId
import logging

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_availability/", response_model=MedicineAvailability)
async def create_medicine_availability(medicine_availability: MedicineAvailability, db=Depends(get_database)):
    try:
        medicine_availability_dict = medicine_availability.dict(by_alias=True)
        result = await db.medicine_availability.insert_one(medicine_availability_dict)
        medicine_availability_dict["_id"] = str(result.inserted_id)
        logger.info(f"Medicine availability created with ID: {medicine_availability_dict['_id']}")
        return medicine_availability_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_availability/", response_model=List[MedicineAvailability])
async def get_all_medicine_availability(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        medicine_availability = await db.medicine_availability.find().skip(skip).limit(limit).to_list(length=limit)
        for item in medicine_availability:
            item["_id"] = str(item["_id"])
        return medicine_availability
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_availability/{id}", response_model=MedicineAvailability)
async def get_medicine_availability(id: str, db=Depends(get_database)):
    try:
        medicine_availability = await db.medicine_availability.find_one({"_id": PyObjectId(id)})
        if medicine_availability:
            medicine_availability["_id"] = str(medicine_availability["_id"])
            return medicine_availability
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_availability/{id}", response_model=MedicineAvailability)
async def update_medicine_availability(id: str, medicine_availability: MedicineAvailability, db=Depends(get_database)):
    try:
        update_result = await db.medicine_availability.update_one({"_id": PyObjectId(id)}, {"$set": medicine_availability.dict(by_alias=True)})
        if update_result.modified_count == 1:
            updated_medicine_availability = await db.medicine_availability.find_one({"_id": PyObjectId(id)})
            if updated_medicine_availability:
                updated_medicine_availability["_id"] = str(updated_medicine_availability["_id"])
                return updated_medicine_availability
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/medicine_availability/{id}", response_model=dict)
async def delete_medicine_availability(id: str, db=Depends(get_database)):
    try:
        delete_result = await db.medicine_availability.delete_one({"_id": PyObjectId(id)})
        if delete_result.deleted_count == 1:
            return {"message": "Medicine availability deleted successfully"}
        raise HTTPException(status_code=404, detail="Medicine availability not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    