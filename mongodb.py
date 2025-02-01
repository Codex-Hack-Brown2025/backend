from dotenv import load_dotenv
load_dotenv()

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoHandler:
  def __init__(self, db_name: str = "codex"):
    self.uri = f"mongodb+srv://nuo-wen-lei:{os.environ['MONGODB_PASSWORD']}@codex.ie4t0.mongodb.net/?retryWrites=true&w=majority&appName=codex"
    # Create a new client and connect to the server
    self.client = MongoClient(self.uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    self.client.admin.command('ping')

    print("mongodb connection successful")

    self.db = self.client.get_database(db_name)
