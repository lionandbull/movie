import queryWorker
import rankWorker
import pprint
import DatabaseDAO
import bson.json_util


def search(query: str):
    dao = DatabaseDAO.DatabaseDAO()

    q = queryWorker.QueryWorker()
    words, index2docs = q.output(dao, query)
    r = rankWorker.RankWorker(dao)
    r.input(words, index2docs)
    docs = r.output()

    return docs


# print(search("a retired spy decided to back to save his daughter life. his daughter got caught by gang"))

# pprint.pprint(search("the"))

