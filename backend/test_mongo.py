from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
print("URI:", uri)

client = MongoClient(uri)
print("SUCCESS:", client.list_database_names())
