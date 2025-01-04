from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Access the environment variables
database_url = os.getenv('MONGO_DB_CONNECTION')
collection_name = os.getenv('MongoDB_DB_NAME')

MONGO_DETAILS = database_url

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[collection_name]

def get_database():
    return database