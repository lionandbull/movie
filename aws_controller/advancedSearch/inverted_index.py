import pickle
import re
#from pattern.vector import stem,PORTER
from PorterStemmer import PorterStemmer


class Index(object):

    def __init__(self):
        self._inverted_index = {}

    def index_dir(self, base_path):

        num_files_indexed = 0

        picklefile = open(base_path, 'rb')
        data = pickle.load(picklefile, encoding='iso-8859-1')

        for movie_id in data:
            index = movie_id
            movie = data[movie_id]

            for text in movie["plot"]:
                tokenize = self.tokenize(text)
                stem = self.stemming(tokenize)

                for term in stem:
                    if term not in self._inverted_index:
                        self._inverted_index[term] = {index: 1}
                    else:
                        if index in self._inverted_index[term]:
                            self._inverted_index[term][index] += 1
                        elif index not in self._inverted_index[term]:
                            self._inverted_index[term][index] = 1

        #         self._documents = list(map(lambda x: x.split("/")[1], self._documents))
        # print(self._inverted_index)
        return num_files_indexed

    def tokenize(self, text):
        s = re.sub('[^0-9a-z]+', ' ', text.lower())
        tokens = [x for x in s.split()]
        return tokens

    def stemming(self, tokens):
        p = PorterStemmer()
        return [p.stem(token, 0, len(token) - 1) for token in tokens]

    def search(self, query):
        result = []
        results = {}
        for word in query:
            tokens = self.tokenize(word)
            stems = self.stemming(tokens)

            if stems[0] in self._inverted_index:
                result = self._inverted_index[stems[0]]
            else:
                result = []

            results[stems[0]] = result
        return results


def main(args):
    index = Index()
    data = index.index_dir('movie_to_story.pickle')
    print(index._inverted_index)
    query = ["man", "whale"]
    results = index.search(query)
    print(results)


if __name__ == "__main__":
    import sys

    main(sys.argv)
