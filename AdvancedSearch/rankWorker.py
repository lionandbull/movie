from typing import List, Dict
from sklearn.feature_extraction.text import TfidfTransformer
from const import LIMIT_DOCS
import numpy as np
from collections import defaultdict
from functools import reduce
#from scipy.special import softmax
from pymongo import MongoClient
import bson.json_util

INDEX_IDS = ['freq-reverse', 'positional']

tfidf = TfidfTransformer()

np.set_printoptions(precision=5)


def getFinalScore(scores: List[float], names: List[str]=None):
    return sum(scores)


class RankWorker(object):
    """docstring for RankWorker
    """

    def __init__(self):
        #self.mworker = mongodbworker
        self.index2docs = {}  # indextype : {word:{docid:freq}}
        self.doc2vecs = {}  # indextype : {doc: feature matrix}
        self.docs2score = {}
        self.ix_to_doc = {}
        self.doc_to_ix = {}
        self.word_to_ix = {}
        self.qwords = []

    def input(self, qwords: List, index2docs: Dict):
        '''

        '''
        self.index2docs = index2docs
        # self.qwords = qwords
        self.word_to_ix = {}
        # for w in self.qwords:

        for w in self.index2docs['freq-reverse'].keys():
            self.qwords.append(w)
            if w not in self.word_to_ix:
                self.word_to_ix[w] = len(self.word_to_ix)

    def precheck(self)->bool:
        """
            whether the index2docs is larger than 0
        """
        flag = True
        if len(self.index2docs) <= 0:
            flag = False
        if len(self.qwords) == 0:
            flag = False
        if max([len(self.index2docs[idx]) for idx in INDEX_IDS]) == 0:
            flag = False
        return flag  # len(self.index2docs) > 0

    def docs2index(self):
        """
        """
        # 统计所有出现过的文档
        for idx in INDEX_IDS:
            for wd in self.word_to_ix.keys():  # for every query word
                if wd not in self.index2docs[idx]:
                    continue
                for d in self.index2docs[idx][wd].keys():  # for every doc id
                    if d not in self.doc_to_ix:
                        self.doc_to_ix[d] = len(self.doc_to_ix)
        # 反向索引
        self.ix_to_doc = {ix: doc for doc, ix in self.doc_to_ix.items()}

    def docs2feature(self):
        """

        """
        # 建立倒排索引下的 文档-词汇频率 矩阵
        doc2wordfreq = [[0] * len(self.word_to_ix)
                        for _ in range(len(self.doc_to_ix))]
        for wd, docDict in self.index2docs['freq-reverse'].items():
            for did, freq in docDict.items():
                # print(self.word_to_ix)
                # print(wd)
                # print("----------")
                x = self.doc_to_ix[did]
                y = self.word_to_ix[wd]
                doc2wordfreq[x][y] = freq
        self.doc2vecs['freq-reverse'] = doc2wordfreq

    def freqRanking(self):
        freqs = [0 for _ in range(len(self.doc_to_ix))]
        for ix, vals in enumerate(self.doc2vecs['freq-reverse']):
            freqs[ix] = sum(vals) / len(vals)
        mean = sum(freqs) / len(freqs)
        diff = max(freqs) - min(freqs)
        return [(f - mean) / diff for f in freqs]

    def docs2position(self):
        # 出现位置初始化为-1，当真有出现的时候，会直接覆盖出现位置的list
        word_doc_post = [[[-1] for __ in range(
            len(self.doc_to_ix))] for ___ in range(len(self.word_to_ix))]

        for wd in self.word_to_ix.keys():
            for doc in self.doc_to_ix.keys():
                if wd not in self.index2docs['positional']:
                    continue
                if doc not in self.index2docs['positional'][wd]:
                    continue
                word_doc_post[self.word_to_ix[wd]][self.doc_to_ix[
                    doc]] = self.index2docs['positional'][wd][doc]
        self.doc2vecs['positional'] = word_doc_post

    def alignment(self, word_doc_post):
        # N = len(self.word_to_ix)  # word
        # M = len(self.doc_to_ix)  # doc
        def comb(place1, place2, coda=' '):
            return [str(p1) + coda + str(p2) for p1 in place1 for p2 in place2]
        # 算分 这里是 直接算距离的方法
        docs_score = [0] * len(self.doc_to_ix)  # {}
        baseline = np.array([i + 1 for i in range(len(self.qwords))])  # 1 by N

        for doc in self.doc_to_ix.keys():
            j = self.doc_to_ix[doc]
            places = [word_doc_post[self.word_to_ix[w]][j]
                      for w in self.qwords]
            vectors = reduce(comb, places)  # length = H
            comb_to_plcs = np.array([list(map(int, vec.split()))
                                     for vec in vectors])  # H by N
            scores = np.dot(baseline, comb_to_plcs.T)  # 1 by H
            docs_score[j] = np.max(scores)  # softmax(scores))  # 1
        mean = sum(docs_score) / len(self.doc_to_ix)
        diff = max(docs_score) - min(docs_score)
        docs_to_score = {doc: (
            docs_score[self.doc_to_ix[doc]] - mean) / diff for doc in self.doc_to_ix.keys()}

        return docs_to_score

    def ranking(self)->List:
        """ The core of this class!
            0. 将检索结果转化成特征向量
            1. 计算不同特征的得分
            2. 计算加权和
            3. 排序
        """
        # 0. 初始化
        # 获得每个index下的doc vector用于计算
        self.docs2index()
        # 文档-分数 字典
        docs2score = defaultdict(list)

        # 1. 计算得分
        # 1.1 计算频率上的得分
        if 'freq-reverse' in INDEX_IDS and len(self.qwords) > 1:
            self.docs2feature()
            tfidfmat = tfidf.fit_transform(self.doc2vecs['freq-reverse'])
            for ix, vec in enumerate(tfidfmat.toarray()):
                if np.square(vec).sum() != 0:
                    score = np.sum(vec) / np.square(vec).sum()
                else:
                    score = 0
                docs2score[self.ix_to_doc[ix]].append(score)

        if 'freq-reverse' in INDEX_IDS and len(self.qwords) == 1:
            self.docs2feature()
            scores = self.freqRanking()
            for ix, s in enumerate(scores):
                docs2score[self.ix_to_doc[ix]].append(s)
            # 1.2 计算不同位置上的得分？
            # ...

        if 'positional' in INDEX_IDS and len(self.qwords) > 1:
            # 对齐算分
            self.docs2position()
            docs_score = self.alignment(self.doc2vecs['positional'])
            for did in self.doc_to_ix:
                docs2score[did].append(docs_score[did])
        # 2. 合计总分
        scoring = []
        ranking = []
        for doc, scores in docs2score.items():
            ranking.append(doc)
            scoring.append(getFinalScore(scores))
        # 3. 根据总分排序
        inds = np.argsort(scoring)
        ranking = np.array(ranking)
        ranking = ranking[inds]
        return ranking[::-1]

    def getDocs(self, docIDs: List)->List:
        """
            get the original docs from database
            docsIDs: the docs id that need to obtain from database
        """
        # 是否限制最大检索数量
        if LIMIT_DOCS:
            nums = min(LIMIT_DOCS, len(docIDs))
        else:
            nums = len(docIDs)

        LOCAL_URL = "mongodb+srv://jack:jackmongodb@cluster0-uagde.mongodb.net"
        mc = MongoClient(LOCAL_URL)
        db = mc['IMDBData']
        c = db['Movies']
        docs = []
        for i in range(nums):
            movie = c.find_one({'imdbID': docIDs[i]})
            if movie == None: continue
            docs.append(movie)
        return docs

    def output(self)->List:
        """
            return the original docs 
        """
        docs = []
        # 检查输入是否合理
        if self.precheck() is False:
            return docs
        # 排序
        docIDs = self.ranking()
        # 获得对应文档
        docs = self.getDocs(docIDs)
        return docs


def testcase():
    '''
    This function is used to generated input data
    '''
    index2docs = {}
    # index2docs['freq-reverse'] = {'man': {'tt1046173': 1, 'tt0119654': 1, 'tt0209475': 3, 'tt0172495': 1, 'tt1272878': 2, 'tt0100405': 1, 'tt0457939': 1, 'tt0056923': 1, 'tt0133093': 2, 'tt1371111': 1, 'tt0258463': 5, 'tt0250797': 4, 'tt0421715': 1, 'tt1261945': 1, 'tt1045658': 1, 'tt0167404': 2, 'tt2024544': 3, 'tt0947798': 1, 'tt0268978': 1, 'tt0119643': 7, 'tt0118564': 3, 'tt0256415': 1, 'tt1877832': 1, 'tt0376994': 1, 'tt1205489': 2, 'tt2194499': 1, 'tt1401152': 1, 'tt0314331': 1, 'tt0127536': 1, 'tt0163025': 1, 'tt0365907': 5, 'tt0083866': 1, 'tt1229822': 1, 'tt0120611': 2, 'tt0120586': 2, 'tt0114814': 3, 'tt0082198': 1, 'tt0316654': 20, 'tt0276751': 1, 'tt0144084': 1, 'tt2923316': 1, 'tt0307987': 1, 'tt0409847': 2, 'tt1013753': 3, 'tt0319061': 1, 'tt1454468': 1, 'tt0993846': 1, 'tt0113497': 2, 'tt0257360': 1, 'tt0109830': 1, 'tt1800241': 2, 'tt1093908': 2, 'tt0372237': 1, 'tt1385826': 1, 'tt1798709': 1, 'tt0083987': 2, 'tt0455824': 1, 'tt0454921': 1, 'tt1178663': 1, 'tt1399103': 1, 'tt0106918': 1, 'tt1790885': 4, 'tt0476964': 1, 'tt0113161': 1, 'tt0349903': 1,
    #                                      'tt0120735': 1, 'tt0478311': 1, 'tt0324554': 3, 'tt1605783': 2, 'tt0412019': 5, 'tt1726592': 4, 'tt0425210': 3, 'tt0068646': 1, 'tt2614684': 2, 'tt0120689': 1, 'tt1068680': 2, 'tt1139328': 2, 'tt0108185': 11, 'tt1228705': 4, 'tt0397078': 1, 'tt1343092': 2, 'tt1570728': 3, 'tt1276104': 2, 'tt0103064': 1, 'tt0218967': 1, 'tt2267998': 2, 'tt0163187': 1, 'tt0104036': 1, 'tt0493464': 5, 'tt1174732': 2, 'tt0480025': 2, 'tt0087892': 1, 'tt0137523': 1, 'tt0343818': 1, 'tt0036775': 4, 'tt0408306': 1, 'tt2294449': 1, 'tt0375679': 9, 'tt0383574': 1, 'tt0988595': 1, 'tt3346224': 1, 'tt0145734': 2, 'tt1598822': 1, 'tt0256380': 1, 'tt0095953': 1, 'tt1229340': 1, 'tt0244353': 1, 'tt0086879': 1, 'tt0118842': 2, 'tt0780571': 2, 'tt0898367': 15, 'tt0112818': 1, 'tt0099685': 2, 'tt0240890': 2, 'tt0388795': 1, 'tt0118715': 2, 'tt0091867': 2, 'tt0109831': 1, 'tt0221027': 1, 'tt1375666': 1, 'tt1535970': 2, 'tt0889583': 3, 'tt1058017': 4, 'tt1001508': 1, 'tt0385752': 1, 'tt0317198': 1, 'tt0120815': 2, 'tt0166924': 8, 'tt0240772': 2, 'tt0452625': 2, 'tt0075314': 2}, 'whale': {'tt0120684': 26}}
    # INDEX_IDS.append('freq-reverse')
    index2docs['positional'] = {'tattoo': {'tt0120586': [377], 'tt1568346': [177], 'tt2294449': [287, 326]}, 'girl': {'tt0281358': [78], 'tt0167404': [333], 'tt0119396': [300], 'tt0119488': [410], 'tt0256415': [660], 'tt1659337': [329], 'tt0242653': [46], 'tt0127536': [326], 'tt0108052': [199], 'tt0365907': [847, 907], 'tt0083866': [225], 'tt0082198': [334, 439], 'tt1114677': [727], 'tt0397535': [11, 66], 'tt1000774': [47], 'tt0866439': [89, 662], 'tt0097165': [273], 'tt0295297': [
        321, 422, 511], 'tt0246772': [313, 449], 'tt0478311': [793], 'tt0335119': [6], 'tt0467406': [305], 'tt0112697': [8, 237], 'tt0107614': [724], 'tt0108399': [48], 'tt0486822': [187], 'tt0118971': [487], 'tt0480025': [75], 'tt0343818': [41], 'tt0375679': [1174], 'tt1598822': [653], 'tt0305711': [444, 504, 508, 535, 541, 602, 647, 723], 'tt2278388': [6, 1295], 'tt0089218': [164], 'tt1535970': [131], 'tt0125439': [84], 'tt0322259': [83], 'tt0452625': [24, 607]}}
    INDEX_IDS.append('positional')
    qwords = ['tattoo', 'girl']

    return qwords, index2docs


def main():
    '''
    This is test case.
    '''

    # get input
    qwords, index2docs = testcase()

    # input into the worker
    rworker.input(qwords, index2docs)
    # get the docs detail of related movie
    docs = rworker.output()
    """ List of pymongo.cursor.Cursor object
    [<pymongo.cursor.Cursor object at 0x11ed1f2e8>, <pymongo.cursor.Cursor object at 0x10f341f28>]
    """

if __name__ == '__main__':
    main()
