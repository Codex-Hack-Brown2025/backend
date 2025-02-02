from typing import Any
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
  
  def get_translations(self, landmark_id: str) -> dict[str, Any]:
    return self.db.get_collection("landmarks").find_one(
      filter = {
        "landmark_id": landmark_id
    })

  def store_translation(self, landmark_id, target_language, new_translation):
    self.db.get_collection("landmarks").update_one(
      filter = {
        "landmark_id": landmark_id
      },
      update = {
        "$set": {
          f"translations.{target_language}": new_translation
        }
      })
  
  def store_landmark(self, landmark_id, original_language, original_translation):
    self.db.get_collection("landmarks").insert_one({
      "landmark_id": landmark_id,
      "original_language": original_language,
      "translations": {
        original_language: original_translation
      }
    })
  
  def get_user(self, user_name: str):
    return self.db.get_collection("users").find_one(
      filter={
        "username": user_name
      }
    )
  
  def create_user(self, user_name: str, language: str, pat: str):
    return self.db.get_collection("users").insert_one({
      "username": user_name,
      "language": language,
      "PAT": pat
    })

