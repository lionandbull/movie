import pymongo

import bson.json_util
import pprint


class DatabaseDAO:
    def __init__(self):
        self.cacheDb = None

    def connectToDatabase(self):
        if self.cacheDb:
            return self.cacheDb
        client = pymongo.MongoClient("mongodb+srv://jack:jackmongodb@cluster0-uagde.mongodb.net")
        self.cacheDb = client['IMDBData']
        return self.cacheDb

    def insertUser(self, event):
        self.cacheDb['User'].insert_one(event)

    

dao = DatabaseDAO()


