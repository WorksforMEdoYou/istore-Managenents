from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from .curd import store, customers, medicineavailable, orders, substitutes, distributors, manufacturers, purchase, sales, stock, customers, medicinemaster, category, users, pricing
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
# from service our bussness model logic
from .Service import store as store_service

app = FastAPI()

# Custom JSON encoder for ObjectId
def json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Override default JSONEncoder with custom JSONEncoder
app.json_encoder = json_encoder

app.include_router(store.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(substitutes.router, prefix="/api") 
app.include_router(distributors.router, prefix="/api")
app.include_router(manufacturers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(purchase.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(medicineavailable.router, prefix="/api")
app.include_router(medicinemaster.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(pricing.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Istore"}

#service 
app.include_router(store_service.router, prefix="/api/service")

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
