from fastapi import FastAPI
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