from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.mysql_schema import StoreDetailsCreate, StoreDetails
from app.models.mysql_models import (StoreDetails as StoreDetailsModel, MedicineMaster as MedicineMasterModel, Manufacturer as ManufacturerModel, Category as CategoryModel)
from app.models.mongodb_models import Order, SaleItem, Stock, MedicineAvailability, Sale
from app.db.mysql import get_db
from app.db.mongodb import get_database
import logging
from sqlalchemy.exc import SQLAlchemyError
from bson import ObjectId

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Create Store - Validate input and insert store details in db with verification status as pending
@router.post("/stores/", response_model=StoreDetails)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    if not store.store_name or not store.license_number or not store.gst_number:
       raise HTTPException(status_code=400, detail="Invalid input")
    try:
        #cheacking for the license_number, cause the license number can be unique
        already_present = db.query(StoreDetailsModel).filter(StoreDetailsModel.license_number == store.license_number).first()
        if already_present:
            raise HTTPException(status_code=400, detail="Store already exists")
        #inserting the store details in db
        db_store = StoreDetailsModel(**store.dict())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

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

from app.models.mongodb_models import Sale 
@router.post("/create/sale/", response_model=Sale)
async def sales_create(sale: Sale, mongo_db=Depends(get_database)):
    try:
        sale_dict = sale.dict(by_alias=True)
        sales_items = sale_dict["sale_items"]
        store_id = sale_dict["store_id"]
        
        for item in sales_items:
            medicine_id = item["medicine_id"]
            quantity = item["quantity"]

            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Invalid quantity")

            # Fetch the medicine stock
            medicine_stock = await mongo_db["stocks"].find_one(
                {"store_id":store_id, "medicine_id": medicine_id, "available_stock": {"$gt": 0}},
                sort=[("batch_detais.expiry_date", 1)]
            )

            if not medicine_stock:
                raise HTTPException(status_code=404, detail="Medicine not available")
            
            batch_id = medicine_stock["_id"]
            expiry_date = medicine_stock["batch_detais"]["expiry_date"]
            available_quantity = medicine_stock["batch_detais"]["batch_quantity"]
            item["expiry_date"]=str(expiry_date)
            if available_quantity <= quantity:
                quantity -= available_quantity
                await mongo_db["stocks"].update_one(
                    {"_id": ObjectId(str(batch_id))},
                    {"$set": {"available_stock": 0, "batch_detais.batch_quantity": 0}}
                )
                await mongo_db["medicine_availability"].update_one(
                    {"store_id": store_id, "medicine_id": medicine_id},
                    {"$set": {"available_quantity": 0}}
                )
            else:
                await mongo_db["stocks"].update_one(
                    {"_id": ObjectId(str(batch_id))},
                    {"$inc": {"available_stock": -quantity, "batch_detais.batch_quantity": -quantity}}
                )
                await mongo_db["medicine_availability"].update_one(
                    {"store_id": store_id, "medicine_id": medicine_id},
                    {"$inc": {"available_quantity": -quantity}}
                )
                quantity = 0
            
        result = await mongo_db["sales"].insert_one(sale_dict)
        sale_dict["_id"] = str(result.inserted_id)

        return sale_dict  # Return the created sale object

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

# List orders
@router.get("/orders/list/")
async def orders_list(mongo_db = Depends(get_database)):
    try:
        session = await mongo_db.client.start_session()
        async with session.start_transaction():
            result=[]
            orders_cursor = mongo_db["orders"].find({"order_status": {"$ne": "delivered"}})
            orders = await orders_cursor.to_list(length=None)
            for order in orders:
                customer_id = str(order["customer_id"])
                order_status = order["order_status"]
                payment_method = order["payment_method"]
                items = len(order["order_items"])
                customers_cursor = mongo_db["customers"].find({"_id": ObjectId(customer_id)})
                customers = await customers_cursor.to_list(length=None)
                for customer in customers:
                    customer_name = customer["name"]
                    doctor_name = customer["doctor_name"]
                    order_list = {
                        "customer_name": customer_name,
                        "doctor_name": doctor_name,
                        "order_status": order_status,
                        "payment_method": payment_method
                    }
                    result.append(order_list)
        return result if len(result)>0 else {"No orders Found"}
    except Exception as e:
        logger.error(f"Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get sales History the status must be Delevered
@router.get("/sales/history/")
async def sales_history(mongo_db = Depends(get_database)):
    try:
        session = await mongo_db.client.start_session()
        async with session.start_transaction():
            customers_cursor = mongo_db["customers"].find()  # Fetch all customers
            result = []
            customers = await customers_cursor.to_list(length=None)
            for customer in customers:
                customer_id = customer["_id"]
                print(f"{customer_id}, {type(customer_id)}")
                orders_cursor = mongo_db["orders"].find({"customer_id": str(customer_id), "order_status": "delivered"})  # Fetch orders with status "delivered"
                orders = await orders_cursor.to_list(length=None)
                for order in orders:
                    sale_data = {
                    "customer_name": customer["name"],
                    "doctor_name": customer["doctor_name"],
                    "status": order["order_status"]
                    }
                    result.append(sale_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No sales found {e}")

# stocks
@router.get("/stocks/")
async def stocks(
    mongo_db = Depends(get_database),
    mysql_db: Session = Depends(get_db)):
    try:
        result = []
        medicine_stocks = mongo_db["stocks"].find()  # getting all the data
        stocks = await medicine_stocks.to_list(length=None)
        for stock in stocks:
            medicine_id = stock["medicine_id"]
            medicine_form = stock["medicine_form"]
            medicines = mysql_db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_id == medicine_id).first()
            if medicines:
                medicine_name = medicines.medicine_name
                medicine_generic_name = medicines.generic_name
                medicine_manufacturer_id = medicines.manufacturer_id
                medicine_category_id = medicines.category_id
            categories = mysql_db.query(CategoryModel).filter(CategoryModel.category_id == medicine_category_id).first()
            if categories:
                category_name = categories.category_name
            manufacturers = mysql_db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == medicine_manufacturer_id).first()
            if manufacturers:
                manufacturer_name = manufacturers.manufacturer_name
            is_medicine_available = mongo_db["medicine_availability"].find({"medicine_id": medicine_id})
            is_medicine = await is_medicine_available.to_list(length=None)
            if is_medicine:
                for medicine_stock in is_medicine:
                    is_stock = "In stock" if (medicine_stock["available_quantity"] > 0) else "Not In Stock"
            medicine_pricing = mongo_db["pricing"].find({"medicine_id": medicine_id})
            medicine_pricing = await medicine_pricing.to_list(length=None)
            if medicine_pricing:
                for medicine_price in medicine_pricing:
                    medicine_mrp = medicine_price["mrp"]  # Corrected line
                    medicine_discount = medicine_price["discount"]  # Corrected line
                    medicine_net_price = medicine_price["net_rate"]  # Corrected line
            medicine_purchase = mongo_db["purchases"].find({"purchase_items.medicine_id": medicine_id})
            medicine_purchase = await medicine_purchase.to_list(length=None)
            for purchase in medicine_purchase:
                for item in purchase["purchase_items"]:
                    batch_id = item["batch_id"]
                    unit_quantity = item["unit_quantity"]
                    package_count = item["package_count"]
                    expiry_date = item["expiry_date"]

                    medicine = {
                        "medicine_id": medicine_id,
                        "medicine_name": medicine_name,
                        "medicine_form": medicine_form,
                        "manufacturer_name": manufacturer_name,
                        "category": category_name,
                        "composition": medicine_generic_name,
                        "expiry_date": expiry_date,
                        "is_stock": is_stock,
                        "unit_quantity": unit_quantity,
                        "package_count": package_count,
                        "mrp": medicine_mrp,
                        "discount": medicine_discount,
                        "net_rate": medicine_net_price,
                        "batch_id": str(batch_id)
                    }
                    result.append(medicine)
        return result         
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Server error {e}")       

# stock Particular Product 
@router.get("/stock/{medicine_id}")
async def get_stock_by_medicine(
    medicine_id: int, 
    mongo_db = Depends(get_database),
    mysql_db: Session = Depends(get_db)
    ):
    try:
        result = []
        if medicine_id:
            #getting thr batch number and expiry date batch wise 
            medicine_stocks = mongo_db.stocks.find({"medicine_id":medicine_id})
            medicine_stocks = await medicine_stocks.to_list(length=None)
            store_id = medicine_stocks["store_id"]
            for batches in medicine_stocks["batch_detais"]:
                batch_number = batches["batch_number"]
                batch_medicine_expiry_date = batches["expiry_date"]
            
            #getting the mrp, discount, Netrate with shop and medicine ids
            medicine_prices = mongo_db.pricing.find({"medicine_id":medicine_id, "store_id":store_id})
            medicine_prices = await medicine_prices.to_list(length=None)
            for price in medicine_prices:
                medicine_mrp = price["mrp"]
                medicine_discount = price["discount"]
                medicine_net_price = price["net_rate"]
            
            # is stock Available
            medicine_available = mongo_db.medicine_availability.find({"store_id":store_id, "medicine_id":medicine_id})
            medicine_available = await medicine_available.to_list(length=None)
            is_available = "In Stock" if medicine_available["available_quantity"]>0 else "Not In Stock"
            
            # packets and units
            medicine_units = mongo_db.purchases.find({"store_id":store_id, "purchase_items.medicine_id":medicine_id})
            medicine_units = await medicine_units.to_list(length=None)
            for units in medicine_units["purchase_items"][medicine_id]:
                unit_quantity = units["unit_quantity"]
                package_count = units["package_count"]
                
            result.append({
                "is Stock": is_available,
                "batch_number": batch_number,
                "expiry_date": batch_medicine_expiry_date,
                "mrp": medicine_mrp,
                "discount": medicine_discount,
                "net_rate": medicine_net_price,
                "unit_quantity": unit_quantity,
                "package_count": package_count
            })


        else:
            return {"message": "Invalid medicine id"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Server error {e}")

# Purchase
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.mongodb import get_database
from ..models.mongodb_models import Purchase
from ..models.mysql_models import Distributor, StoreDetails
from ..db.mysql_session import get_db
from datetime import datetime

#Get purchases by date range
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
