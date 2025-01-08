from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Access the environment variables
#MONGO_DETAILS = os.getenv('MONGO_DB_CONNECTION')
MONGO_DETAILS = "mongodb://localhost:27017"
#collection_name = os.getenv('MongoDB_DB_NAME')
collection_name = "istores"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[collection_name]

def get_database():
    return database