from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.stores.StoreDetailsSchema import StoreDetailsCreate, StoreDetails
from app.models.stores.Mysql.mysql_models import (StoreDetails as StoreDetailsModel, MedicineMaster as MedicineMasterModel, Manufacturer as ManufacturerModel, Category as CategoryModel)
from app.models.stores.MongoDb.mongodb_models import SaleItem, Sale, Purchase
from app.db.mysql import get_db
from app.db.mongodb import get_database
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from bson import ObjectId
from app.models.stores.Mysql.mysql_models import Substitutes as SubstituteModel
from app.models.stores.Mysql.mysql_models import User as UserModel, Distributor
from app.schemas.stores.UserSchema import UserCreate
from app.utils import get_password_hash
from app.Service.stores.store import store_validation, create_store_record

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Create Store - Validate input and insert store details in db with verification 
@router.post("/stores/", response_model=StoreDetails, status_code=status.HTTP_201_CREATED)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    if not store.store_name or not store.license_number or not store.gst_number:
       raise HTTPException(status_code=400, detail="Invalid input")
    try:
        #cheacking for the license_number, cause the license number can be unique
        already_present = store_validation(store, db)
        if already_present != "unique":
            raise HTTPException(status_code=400, detail="Store already exists")
        #inserting the store details in db
        db_store = create_store_record(store, db)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

# Create Sales - Sales need to be created by executing the logic for stock verification and updates
""" @router.post("/sales/")
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
    
    return {"status": "Sales created successfully"} """

# If iam using only one sales item it throws an error and some majority data is getting lost so i have to use the Sale model
@router.post("/create/sale/", response_model=Sale, status_code=status.HTTP_201_CREATED)
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
@router.get("/orders/list/", status_code=status.HTTP_200_OK)
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
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "doctor_name": doctor_name,
                        "order_status": order_status,
                        "payment_method": payment_method,
                        "no_of_items": items
                    }
                    result.append(order_list)
        return result if len(result)>0 else {"No orders Found"}
    except Exception as e:
        logger.error(f"Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get sales History the status must be Delevered
@router.get("/sales/history/", status_code=status.HTTP_200_OK)
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
# Get all stocks
@router.get("/stocks/", status_code=status.HTTP_200_OK)
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

# stock Particular Product by medicine_id
@router.get("/stocks/{medicine_id}/", status_code=status.HTTP_200_OK)
async def get_stock_by_medicine(
    medicine_id: int, 
    mongo_db: Session = Depends(get_database),
    mysql_db: Session = Depends(get_db)
):
    try:
        if not medicine_id:
            raise HTTPException(status_code=400, detail="Invalid medicine ID")
        
        # result
        result=[]
        
        #batches
        batches = []
        # Fetch batches of the medicine
        medicine_batches = await mongo_db.stocks.find({"medicine_id": medicine_id}).to_list(length=None)
        if not medicine_batches:
            raise HTTPException(status_code=404, detail="No batches found for the given medicine ID")

        for medicine_batch in medicine_batches:
            store_id = medicine_batch.get("store_id")
            batch_available_stock = "In Stock" if medicine_batch.get("available_stock", 0) > 0 else "Not In Stock"

            batch_detais = medicine_batch.get("batch_detais")

            # Ensure batch_detais is iterable
            if isinstance(batch_detais, dict):
                batch_detais = [batch_detais]
            elif not isinstance(batch_detais, list):
                raise HTTPException(status_code=400, detail="Invalid batch_detais format")

            for batch in batch_detais:
                batch_number = batch.get("batch_number")
                expiry_date = batch.get("expiry_date")

                # Fetch price details
                batch_medicine_price = await mongo_db.pricing.find(
                    {"store_id": store_id, "medicine_id": medicine_id}
                ).to_list(length=None)
                if not batch_medicine_price:
                    continue

                price = batch_medicine_price[0]  # Assuming only one entry per store_id and medicine_id
                mrp = price.get("mrp", 0)
                discount = price.get("discount", 0)
                net_rate = price.get("net_rate", 0)

                # Fetch purchase details
                medicine_quantities = await mongo_db.purchases.find(
                    {"store_id": store_id, "purchase_items.medicine_id": medicine_id}
                ).to_list(length=None)
                
                unit_quantity = package_count = 0
                for purchase in medicine_quantities:
                    if not isinstance(purchase.get("purchase_items"), list):
                        continue

                    for item in purchase["purchase_items"]:
                        if item.get("medicine_id") == medicine_id:
                            unit_quantity = item.get("unit_quantity", 0)
                            package_count = item.get("package_count", 0)

                batches.append({
                    "store_id": store_id,
                    "is_stock": batch_available_stock,
                    "batch_number": batch_number,
                    "expiry_date": expiry_date,
                    "mrp": mrp,
                    "discount": discount,
                    "net_rate": net_rate,
                    "unit_quantity": unit_quantity,
                    "package_count": package_count
                })
        
        # Purchases
        purchases = []
        # Fetch purchase details
        medicine_purchases_cursor = mongo_db.purchases.find({"purchase_items.medicine_id": medicine_id})
        medicine_purchases = await medicine_purchases_cursor.to_list(length=None)
        for purchaseed_medicine in medicine_purchases:
            purchase_store_id = purchaseed_medicine["store_id"]
            purchase_date = str(purchaseed_medicine["purchase_date"])
            purchase_distributor_id = purchaseed_medicine["distributor_id"]
            
            #distributor_name
            purchase_distributors = mysql_db.query(Distributor).filter(Distributor.distributor_id == purchase_distributor_id).first()
            if purchase_distributors:
                purchase_distributor_name = purchase_distributors.distributor_name
            
            for purchse_item in purchaseed_medicine["purchase_items"]:
                if purchse_item["medicine_id"] == medicine_id:
                    purchase_batch_id = purchse_item["batch_id"]
                    purchse_medicine_price = purchse_item["price"]
                    purchase_unit_quantity = purchse_item["quantity"]
                    purchase_expiry_date = str(purchse_item["expiry_date"])
            
                    purchase_batch = await mongo_db.stocks.find_one({"_id": ObjectId(str(purchase_batch_id))})
                    if purchase_batch:
                        batch_detais = purchase_batch["batch_detais"]
                        if isinstance(batch_detais, dict):
                            batch_detais = [batch_detais]
                        for batch_detail in batch_detais:
                            purchase_batch_number = batch_detail["batch_number"]
                            
                            purchases.append({
                                "store_id": purchase_store_id,
                                "purchase_date": purchase_date,
                                "distributor_name": purchase_distributor_name,
                                "batch_number": purchase_batch_number,
                                "price": purchse_medicine_price,
                                "quantity": purchase_unit_quantity,
                                "expiry_date": purchase_expiry_date
                            })
                    
        #sales
        sales = []
        # Fetch sales details
        medicine_sales_cursor = mongo_db.sales.find({"sale_items.medicine_id": medicine_id})
        saled_medicines = await medicine_sales_cursor.to_list(length=None)
        for saled_medicine in saled_medicines:
            sale_store_id = saled_medicine["store_id"]
            sale_date = str(saled_medicine["sale_date"])
            sale_invoice_number = saled_medicine["invoice_id"]
            
            saled_customer_id = saled_medicine["customer_id"]
            medicine_saled_customer = await mongo_db.customers.find_one({"_id": ObjectId(str(saled_customer_id))})
            if medicine_saled_customer:
                customer_name = medicine_saled_customer["name"]
                doctor_name = medicine_saled_customer["doctor_name"]
            
            for saled_items in saled_medicine["sale_items"]:
                if saled_items["medicine_id"] == medicine_id:
                    sale_batch_id = saled_items["batch_id"]
                    sale_medicine_price = saled_items["price"]
                    sale_unit_quantity = saled_items["quantity"]
                    sale_expiry_date = str(saled_items["expiry_date"])
                    
                    sale_batch = await mongo_db.stocks.find_one({"_id": ObjectId(str(sale_batch_id))})
                    if sale_batch:
                        batch_detais = sale_batch["batch_detais"]
                        if isinstance(batch_detais, dict):
                            batch_detais = [batch_detais]
                        for batch_detail in batch_detais:
                            sale_batch_number = batch_detail["batch_number"]
                            
                            sales.append({
                                "store_id": sale_store_id,
                                "sale_date": sale_date,
                                "invoice_number": sale_invoice_number,
                                "customer_name": customer_name,
                                "doctor_name": doctor_name,
                                "batch_number": sale_batch_number,
                                "mrp": sale_medicine_price,
                                "quantity": sale_unit_quantity,
                                "expiry_date": sale_expiry_date
                            })
        
        # Substitute Medicine
        substitute_medicine = []
        # Fetch substitute medicine details
        medicine_substitutes = mysql_db.query(SubstituteModel).filter(SubstituteModel.medicine_id == medicine_id).all()
        for substitute in medicine_substitutes:
            substitute_medicine_name = substitute.substitute_medicine
    
            substitute_medicine_medicine_master = mysql_db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == substitute_medicine_name).first()
            if substitute_medicine_medicine_master:
                medicines_id = substitute_medicine_medicine_master.medicine_id
        
                substitute_manufacturer_id = substitute_medicine_medicine_master.manufacturer_id
                substitute_manufacturer = mysql_db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_id == substitute_manufacturer_id).first()
                if substitute_manufacturer:
                    substitute_manufacturer_name = substitute_manufacturer.manufacturer_name
        
            substitute_medicine_purchases = mongo_db.purchases.find({"purchase_items.medicine_id": medicines_id})
            substitute_medicine_purchases = await substitute_medicine_purchases.to_list(length=None)
            if substitute_medicine_purchases:
                for substitute_medicine_purchase in substitute_medicine_purchases:
                    substitute_medicine_store_id = substitute_medicine_purchase["store_id"]
                    for item in substitute_medicine_purchase["purchase_items"]:
                        if item["medicine_id"] == medicines_id:
                            substitute_medicine_unit = item["unit_quantity"]
                            substitute_medicine_unit_price = item["price"]
   
                substitute_medicine_available = mongo_db.medicine_availability.find({"medicine_id": medicines_id, "store_id": substitute_medicine_store_id})
                substitute_medicine_available = await substitute_medicine_available.to_list(length=None)
                if substitute_medicine_available:
                    is_substitute_medicine_available = "In Stock" if substitute_medicine_available[0]["available_quantity"] > 0 else "Not In Stock"
            
                substitute_medicine_price = mongo_db.pricing.find({"medicine_id": medicines_id, "store_id": substitute_medicine_store_id})
                substitute_medicine_price = await substitute_medicine_price.to_list(length=None)
                if substitute_medicine_price:
                    substitute_medicine_prices_mrp = substitute_medicine_price[0]["mrp"]
                
                substitute_medicine.append({
                "substitute_medicine_store_id": substitute_medicine_store_id,
                "substitute_medicine_name": substitute_medicine_name,
                "substitute_manufacturer_name": substitute_manufacturer_name,
                "substitute_medicine_unit": substitute_medicine_unit,
                "substitute_medicine_unit_price": substitute_medicine_unit_price,
                "is_substitute_medicine_available": is_substitute_medicine_available,
                "substitute_medicine_mrp_price": substitute_medicine_prices_mrp
                })
            
        result.append({
            "batches": batches,
            "purchases": purchases,
            "sales": sales,
            "substitutes": substitute_medicine
        })
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Server error: {e}")

# Purchase
#Get purchases by date range
@router.get("/purchases/", status_code=status.HTTP_200_OK)
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
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
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
            shop = mysql_db.query(StoreDetailsModel).filter(StoreDetailsModel.store_id == shop_id).first()
            if shop:
                shop_gst = shop.gst_number

                # Fetch distributor details
                distributor = mysql_db.query(Distributor).filter(Distributor.distributor_id == distributor_id).first()
                if distributor:
                    distributor_name = distributor.distributor_name

                    # Append the formatted data to the result
                    result.append({
                        "shop_id": shop_id,
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
@router.post("/purchase/create/", status_code=status.HTTP_201_CREATED)
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
@router.put("/users/{user_id}", status_code=status.HTTP_200_OK)
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
