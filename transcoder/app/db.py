import os

from pymongo import MongoClient

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("MONGO_DB")
        _client = MongoClient(uri)[db_name]
    return _client
