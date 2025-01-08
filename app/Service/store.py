from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..schemas.mysql_schema import StoreDetailsCreate, StoreDetails
from ..models.mysql_models import (StoreDetails as StoreDetailsModel, MedicineMaster as MedicineMasterModel)
from ..models.mongodb_models import Order, SaleItem, Stock, MedicineAvailability, Sale
from ..db.mysql_session import get_db
from ..db.mongodb import get_database
import logging
from sqlalchemy.exc import SQLAlchemyError

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Create Store - Validate input and insert store details in db with verification status as pending
@router.post("/stores/", response_model=StoreDetails)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    if store.store_name == "string" or store.license_number == "string" or store.gst_number == "string":
        raise HTTPException(status_code=400, detail="Invalid input")
    try:
        db_store = StoreDetailsModel(**store.dict())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

# List Orders - Fetch order list which is not in delivered status with details
@router.get("/orders/")
async def list_orders(mongo_db = Depends(get_database)):
    orders = mongo_db["orders"].find({"order_status": {"$ne": "delivered"}})
    result = []
    async for order in orders:
        order_data = {
            "customer_name": order["customer_name"],
            "payment_status": order["payment_status"],
            "total_items": order["total_items"],
            "order_status": order["order_status"],
            "medicines": []
        }
        for item in order["order_items"]:
            order_data["medicines"].append({
                "medicine_name": item["medicine_name"],
                "quantity": item["quantity"],
                "price": item["price"],
                "total_cost": item["quantity"] * item["price"]
            })
        result.append(order_data)
    return result

# Create Sales - Sales need to be created by executing the logic for stock verification and updates
@router.post("/sales/")
async def create_sales(sales: List[SaleItem], mongo_db = Depends(get_database)):
    async with mongo_db.client.start_session() as s:
        async with s.start_transaction():
            for item in sales:
                total_quantity = item.quantity
                stock_batches = mongo_db["stock"].find({"medicine_id": item.medicine_id, "available_stock": {"$gt": 0}}).sort("expiry_date")
                
                async for batch in stock_batches:
                    if total_quantity <= 0:
                        break
                    if batch["available_stock"] <= total_quantity:
                        total_quantity -= batch["available_stock"]
                        await mongo_db["stock"].update_one({"_id": batch["_id"]}, {"$set": {"available_stock": 0}})
                    else:
                        await mongo_db["stock"].update_one({"_id": batch["_id"]}, {"$inc": {"available_stock": -total_quantity}})
                        total_quantity = 0
                    
                    sale_item = SaleItem(
                        medicine_id=item.medicine_id, 
                        batch_id=batch["_id"], 
                        quantity=batch["available_stock"] if batch["available_stock"] <= item.quantity else item.quantity, 
                        price=item.price,
                        expiry_date=batch["expiry_date"]
                    )
                    await mongo_db["sales"].insert_one(sale_item.dict())
                
                if total_quantity > 0:
                    raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Update medicine_availability
            for item in sales:
                await mongo_db["medicine_availability"].update_one(
                    {"medicine_id": item.medicine_id}, 
                    {"$inc": {"available_quantity": -item.quantity}}
                )
    
    return {"status": "Sales created successfully"}

# Get sales History the status must be Delevered
@router.get("/sales/history/")
async def sales_history(mongo_db = Depends(get_database)):
    session = await mongo_db.client.start_session()
    async with session.start_transaction():
        customers_cursor = mongo_db["customers"].find()  # Fetch all customers
        result = []
        customers = await customers_cursor.to_list(length=None)
        print(customers)
        for customer in customers:
            customer_id = customer["_id"]
            print(f"{customer_id}, {type(customer_id)}")
            orders_cursor = mongo_db["orders"].find({"customer_id": customer_id, "order_status": "delivered"})  # Fetch orders with status "delivered"
            orders = await orders_cursor.to_list(length=None)
            for order in orders:
                sale_data = {
                    "customer_name": customer["name"],
                    "doctor_name": customer["doctor_name"],
                    "status": order["order_status"],
                    "order_date": order["order_date"],
                    "payment_method": order["payment_method"],
                    "total_amount": order["total_amount"],
                    "order_items": order["order_items"]
                }
                result.append(sale_data)
    return result

# Stocks
@router.get("/stocks/{medicine_id}")
async def get_details_by_medicine(
    mongo_db=Depends(get_database),
    mysql_db: Session = Depends(get_db),
    medicine_id= int):
    result=[]
    # Purchases
    purchases_cursor = mongo_db["purchases"].find({"medicine_id": medicine_id})


# Purchase
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.mongodb import get_database
from ..models.mongodb_models import Purchase
from ..models.mysql_models import Distributor, StoreDetails
from ..db.mysql_session import get_db
from datetime import datetime

#Get purchases by daterange
@router.get("/purchases/")
async def get_purchases_by_date_range(
    mongo_db=Depends(get_database),
    mysql_db: Session = Depends(get_db),
    start_date: str = None,
    end_date: str = None
):
    try:
        # Prepare the result list
        result = []

        if start_date and end_date:
            # Parse the start and end dates
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Fetch purchases from MongoDB within the date range
            purchases = await mongo_db.purchases.find({
                "purchase_date": {"$gte": start_date, "$lte": end_date}
            }).to_list(length=None)
        else:
            # Fetch all purchases from MongoDB
            purchases = await mongo_db.purchases.find().to_list(length=None)

        # Iterate through each purchase
        for purchase in purchases:
            shop_id = purchase['store_id']
            distributor_id = purchase['distributor_id']
            total_amount = purchase['total_amount']
            total_items = len(purchase['purchase_items'])

            # Fetch shop details
            shop = mysql_db.query(StoreDetails).filter(StoreDetails.store_id == shop_id).first()
            if shop:
                shop_gst = shop.gst_number

                # Fetch distributor details
                distributor = mysql_db.query(Distributor).filter(Distributor.distributor_id == distributor_id).first()
                if distributor:
                    distributor_name = distributor.distributor_name

                    # Append the formatted data to the result
                    result.append({
                        "shop_gst": shop_gst,
                        "distributor_name": distributor_name,
                        "total_amount": total_amount,
                        "total_items": total_items
                    })

        # Return the result
        return result

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No purchases found {e}")
            
#creating the manual purchase
@router.post("/purchase/create/")
async def create_purchase(purchase: Purchase, db=Depends(get_database)):
    try:
        purchase_dict = purchase.dict(by_alias=True)
        #checking for the expiry dates of a purchased medicine
        expiry_dates = [item['expiry_date'] for item in purchase_dict['purchase_items']]
        for date in expiry_dates:
            if date < datetime.now().strftime('%Y-%m-%d'):
                raise HTTPException(status_code=400, detail="Expiry date is must be grater than today's date")
        
        result = await db.purchases.insert_one(purchase_dict)
        purchase_dict["_id"] = str(result.inserted_id)
        return purchase_dict
    
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

# Users
from ..db.mysql_session import get_db
from ..models.mysql_models import User as UserModel, StoreDetails as StoreDetailsModel
from ..schemas.mysql_schema import UserCreate
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        # User update
        db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = get_password_hash(user.password_hash)
        db_user.username = user.username
        db_user.password_hash = hashed_password
        db_user.role = user.role
        db_user.store_id = user.store_id
        
        # Update the store
        store_id = user.store_id
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        for key, value in store.dict().items():
            setattr(db_store, key, value)

        # Commit the changes
        db.commit()
        db.refresh(db_user)
        db.refresh(db_store)
        return {"message": "User updated successfully", "user": db_user, "store": db_store}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
