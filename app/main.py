from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from .curd import (store, substitutes, distributors, manufacturers, orders, purchase, sales, stock)

app = FastAPI()

app.include_router(store.router, prefix="/api")
app.include_router(substitutes.router, prefix="/api") 
app.include_router(distributors.router, prefix="/api")
app.include_router(manufacturers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(purchase.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(stock.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Istore"}

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
