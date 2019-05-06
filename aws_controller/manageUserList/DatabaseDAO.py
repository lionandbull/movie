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

    def addToFavorite(self, email, title):
        self.cacheDb['User'].update_one(
            {"email": email},
            {"$addToSet": {"favorite": {"$each": [title]}}}
        )

    def rateMovie(self, email, title, rate):
        rate = int(rate)
        if rate == -1:
            self.cacheDb['User'].update_one(
                {"email": email},
                {"$pull": {'ratedMovies': {"title": title}}}
            )
        elif rate == 0:
            for item in self.cacheDb['User'].find(
                {"$and": [
                    {"email": email}
                ]},
                {"_id": 0, "ratedMovies": {"$elemMatch": {"title": title}}}
            ):
                if item == {}:
                    return None
                return item['ratedMovies'][0]['rate']
        else:
            self.cacheDb['User'].update_one(
                {"email": email, "ratedMovies": {"$not": {"$elemMatch": {"title": title}}}},
                {"$push": {"ratedMovies": {"title": title, "rate": rate}}}
            )
            self.cacheDb['User'].update_one(
                {"email": email, "ratedMovies.title": title},
                {"$set": {"ratedMovies.$.rate": rate}}
            )

    def addToWatchlist(self, email, title):
        self.cacheDb['User'].update_one(
            {"email": email},
            {"$addToSet": {"watchlist": {"$each": [title]}}}
        )

    def whetherInList(self, email, title, type):
        if type == "favorite":
            cursor = self.cacheDb['User'].find({"favorite": title})
            for item in cursor:
                if item:
                    return True
            return False


        elif type == "watchlist":
            cursor = self.cacheDb['User'].find({"watchlist": title})
            for item in cursor:
                if item:
                    return True
            return False
    def removeFavorite(self, email, title):
        self.cacheDb['User'].update_one(
            {"email": email},
            {"$pull": {'favorite': title}}
        )

    def removeWatchlist(self, email, title):
        self.cacheDb['User'].update_one(
            {"email": email},
            {"$pull": {'watchlist': title}}
        )

    def getFavorite(self, email, start, end):
        res = []
        cursor = self.cacheDb['User'].find({"email": email},
                                      {"favorite": {"$slice": [int(start), int(end)]}, "watchlist": 0, "email": 0, "nickname": 0})
        for doc in cursor:
            for movie in doc["favorite"]:
                res.append(self.cacheDb['Movies'].find_one({"Title": movie}))

        return bson.json_util.dumps(res)

    def getWatchlist(self, email, start, end):
        res = []
        cursor = self.cacheDb['User'].find({"email": email},
                                           {"watchlist": {"$slice": [int(start), int(end)]}, "favorite": 0, "email": 0,
                                            "nickname": 0})
        for doc in cursor:
            for movie in doc["watchlist"]:
                res.append(self.cacheDb['Movies'].find_one({"Title": movie}))

        return bson.json_util.dumps(res)

    def countList(self, type, email):
        if type == "favorite":
            cursor = self.cacheDb['User'].find({"email": email})
            for item in cursor:
                return len(item["favorite"])

        elif type == "watchlist":
            cursor = self.cacheDb['User'].find({"email": email})
            for item in cursor:
                return len(item["watchlist"])


dao = DatabaseDAO()
dao.connectToDatabase()

print(dao.rateMovie("liuweixi0819@gmail.com", "The Mountai", "0"))
# dao.removeFavorite("liuweixi0819@gmail.com", "Ljuset håller mig sällskap")
# print(dao.whetherInList("liuweixi0819@gmail.com", "Don's Plum", "watchlist"))
# dao.addToFavorite("qwe")

# print(dao.getOneMovie("Albela"))
# print(dao.getMovieFromTo(1,5))
# print(dao.getMovieFromTo("Drama",1,5))
# pprint.pprint(dao.getTopRated(10))

