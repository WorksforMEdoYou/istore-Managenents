from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.mongodb import get_database
from app.models.store_mongodb_models import MedicineAvailability
import logging
from app.crud.medicine_availability import create_medicine_availability_collection, get_medicine_availability_collection, update_medicine_availability_collection, delete_medicine_availability_collection

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_availability/", response_model=MedicineAvailability, status_code=status.HTTP_201_CREATED)
async def create_medicine_availability(medicine_availability: MedicineAvailability, db=Depends(get_database)):
    try:
        medicine_availability_dict = await create_medicine_availability_collection(medicine_availability=medicine_availability, db=db)
        return medicine_availability_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_availability/", response_model=List[MedicineAvailability], status_code=status.HTTP_200_OK)
async def get_all_medicine_availability(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        medicine_availability = await db.medicine_availability.find().skip(skip).limit(limit).to_list(length=limit)
        for item in medicine_availability:
            item["_id"] = str(item["_id"])
        return medicine_availability
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_availability/{id}", response_model=MedicineAvailability, status_code=status.HTTP_200_OK)
async def get_medicine_availability(id: str, db=Depends(get_database)):
    try:
        medicine_availability = await get_medicine_availability_collection(medicine_availability_id=id, db=db)
        return medicine_availability
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_availability/{id}", response_model=MedicineAvailability, status_code=status.HTTP_200_OK)
async def update_medicine_availability(id: str, medicine_availability: MedicineAvailability, db=Depends(get_database)):
    try:
        update_result = await update_medicine_availability_collection(medicine_availability_id=id, medicine_availability=medicine_availability, db=db)
        return update_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/medicine_availability/{id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_medicine_availability(id: str, db=Depends(get_database)):
    try:
        delete_result = await delete_medicine_availability_collection(medicine_availability_id=id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    