import pymongo

class Conn:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://jack:jackmongodb@cluster0-uagde.mongodb.net")
        self.db = self.client['IMDBData']

    def getConn(self):
        return self.db


