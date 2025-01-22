from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers.stores import store, customers, medicineavailable, orders, substitutes, distributors, manufacturers, purchase, sales, stock, customers, medicinemaster, category, users, pricing
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import logging
# from service our bussness model logic
from app.routers.stores.service import service_store

app = FastAPI()

# Custom JSON encoder for ObjectId
def json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Override default JSONEncoder with custom JSONEncoder
app.json_encoder = json_encoder

app.include_router(store.router, prefix="/api", tags=["Store"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(substitutes.router, prefix="/storeapi", tags=["Substitutes"]) 
app.include_router(distributors.router, prefix="/storeapi", tags=["Distributors"])
app.include_router(manufacturers.router, prefix="/storeapi", tags=["Manufacturers"])
app.include_router(orders.router, prefix="/storeapi", tags=["Orders"])
app.include_router(purchase.router, prefix="/storeapi", tags=["Purchase"])
app.include_router(sales.router, prefix="/storeapi", tags=["Sales"])
app.include_router(stock.router, prefix="/storeapi", tags=["Stock"])
app.include_router(customers.router, prefix="/storeapi", tags=["Customers"])
app.include_router(medicineavailable.router, prefix="/storeapi", tags=["Medicine Available"])
app.include_router(medicinemaster.router, prefix="/storeapi", tags=["Medicine Master"])
app.include_router(category.router, prefix="/storeapi", tags=["Category"])
app.include_router(pricing.router, prefix="/storeapi", tags=["Pricing"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

# Startup Event
@app.on_event("startup")
async def on_startup():
    logger.info("App is starting...")
# Initialize database connection
@app.get("/")
def read_root():
    return {"message": "Welcome to the Istore"}

#service 
app.include_router(service_store.router, prefix="/storeapi/service", tags=["Service"])

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
