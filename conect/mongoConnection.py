from pymongo import MongoClient
import os

class MongoConnection:
    _client = None
    _db = None

    @classmethod
    def get_database(cls):
        if cls._db is None:
            password = os.getenv("MONGO_PASS")

            uri = f"mongodb://admin:ADMINPASS@192.168.0.108:27017/?authSource=admin"

            cls._client = MongoClient(uri)
            cls._db = cls._client["miapp"]

        return cls._db