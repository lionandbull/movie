import queryWorker
# import mongodbWorker
import rankWorker
import pprint

import bson.json_util


def search(query: str):
    q = queryWorker.QueryWorker()
    words, index2docs = q.output(query)
    #m = mongodbWorker.MongodbWorker()
    r = rankWorker.RankWorker()
    r.input(words, index2docs)
    docs = r.output()


    return docs


# print(search("the"))

pprint.pprint(search("a retired spy decided to back to save his daughter life. his daughter got caught by gang"))

