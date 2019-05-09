import pymongo

class PSearch():

    def search_position(self, query, dao):
        results = {}

        # client = pymongo.MongoClient(
        #     "mongodb://jack:jackmongodb@cluster0-shard-00-00-uagde.mongodb.net:27017,cluster0-shard-00-01-uagde.mongodb.net:27017,cluster0-shard-00-02-uagde.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
        # db = client['IMDBData']
        dao.connectToDatabase()
        db = dao.cacheDb
        collection = db['Movies_1']
        for word in query:
            query = {word: {"$exists": True}}
            cursor = collection.find(query, {"_id": 0})
            for i in cursor:
                results.update(i)
            return results


def main(args):
    index = PSearch()
    query = ["man"]
    results = index.search_position(query)

    print(results)


if __name__ == "__main__":
    import sys

    main(sys.argv)
