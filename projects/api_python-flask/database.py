import os
import pymongo
from pymongo import MongoClient

class Database:
    def connect():
        client = MongoClient(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            username=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            authSource=os.getenv('DB_AUTH')
        )
        database = os.getenv('DB_DATABASE')
        db = client[database]
        return db