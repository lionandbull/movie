#from collection import defualtdict
from typing import List, Dict
from preprocess import Processor
from search_inverted import Search
from search_position import PSearch

class QueryWorker(object):
    """docstring for QueryWorker
        USAGE:
        from mongodbWorker import MongodbWorker
        mworker = MongodbWorker()

        qworker = QueryWorker(mworker)
        qworker.input(query)
        index2docs = qworker.output()

        -> index2docs is what you need
    """

    def __init__(self, mongodbworker=None):
        pass

    def wordIndex(self, dao, words: List[str])->Dict:
        """
            using inverted file index of each word
        """
        return Search().search_inverted(words, dao)

    def positionIndex(self, words: List[str], dao)->Dict:
        """
            using inverted zone index of each word
        """
        return PSearch().search_position(words, dao)

    def output(self, dao, text:str)->Dict:
        """
            return the doc ids for querying
        """
        index2docs = {}
        words = Processor().do(text)
        #print(words)
        index2docs['freq-reverse'] = self.wordIndex(dao, words)
        index2docs['positional'] = self.positionIndex(words, dao)
        return words, index2docs

def main():
    query = 'the'
    words, index2docs = QueryWorker().output(query)
    #print(index2docs)

if __name__ == '__main__':
    main()

