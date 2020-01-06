#coding = 'utf-8'

import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import operator
from pymongo import MongoClient
import re
from dateutil import parser
import datetime
from bson import ObjectId


class MMR(object):
    '''
    用MMR算法进行文本摘要处理 （也是textrank算法的变体，在textrank基础上增加了一部分）
    选择出来的句子最大程度的能够和全文所有句子相似度最高，但并不代表该句能最好的概括全文
    不建议使用于新闻筛选系统，建议作为文本搜索和挖掘的算法使用
    '''
    def __init__(self):
        '''
        初始化
        '''
        self.t = datetime.datetime.now()
        self.t_1 = self.t
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name]
        f = open('./References/stop.txt','r').readlines()
        self.stop = [i.replace('\n','') for i in f]
        time_now = self.db.times.find({})
        sys_t = [i['time'] for i in time_now][0]
        self.t_delta = str(self.str2time(sys_t) + datetime.timedelta(days=1))[:10]
        self.t = [str(self.t_1)[:10], str(self.t_delta)]

    def str2time(self, date):
        '''
        将2018-10-10这样的格式的日期转换为时间
        :param date: 日期，格式必须是"YYYY-MM-DD"
        :return: 时间格式
        '''
        datetime_struct = parser.parse(date)
        return datetime_struct

    def clean_data(self, sentence):
        '''
        清理停用词
        :param sentence: 一个句子
        :return: 去除了停用词和标点符号的，已经被分词的句子
        '''
        cut_sentence = jieba.lcut(sentence)
        seg_list = [i.lower() for i in cut_sentence if i not in self.stop]

        return " ".join(seg_list)

    def cal_sim(self, sentence, document):
        '''
        计算相似度，计算的是目标句和文本中其余的每一个句子的余弦相似
        :param sentence: 目标句
        :param document: 除目标句以外的其余句子组成的文本
        :return:
        '''
        if document == []:
            return 0
        vocab = {}
        for word in sentence.split(' '):
            vocab[word] = 0 #构造关键词词典

        document_in_one_sentence = ''
        for t in document:
            document_in_one_sentence += (t + ' ') # 没有了目标句的剩余文本
            for word in t.split(' '):
                vocab[word] = 0

        cv = CountVectorizer(vocabulary=vocab.keys()) # 转为词典索引

        doc_vec = cv.fit_transform([document_in_one_sentence]) # 转为词向量
        sentence_vec = cv.fit_transform([sentence]) # 目标句也转为向量
        return cosine_similarity(doc_vec, sentence_vec)[0][0] # 计算余弦相似度

    def work_flow(self, text, ratio = 0.2, alpha = 0.7):
        '''
        工作流
        :param text: 文本
        :param ratio: 摘要句占目标文本的比例
        :param alpha: 是否连成图的边的阈值
        :return:
        '''
        sentences = []
        clean = []
        origin_sen_dict = {}
        sen_order = []

        texts = re.split(r'[。，；\s！？]',text)

        iterT = 0
        for line in texts:
            cl = self.clean_data(line)
            sentences.append(line) # 原始句子集合
            clean.append(cl) # 分词后的句子集合
            origin_sen_dict[cl] = line # 设立一个字典，将分词前后的句子对应起来
            sen_order.append((line.lstrip(' '), iterT)) # 保留句子语序
            iterT += 1

        set_clean = set(clean) # 去掉重复的句子
        scores = {}

        for data in clean:
            temp_doc = set_clean - set([data]) # 将句子集合去掉目标句
            score = self.cal_sim(data, list(temp_doc)) # 计算该目标句和文本的相似度
            scores[data] = score # 保留句子和相似度，存于字典中

        n = int(ratio*len(sentences)) # 迭代次数由摘要大小决定
        alpha = alpha
        summary = []
        while n > 0:
            mmr = {}
            for sentence in scores.keys():
                if not sentence in summary:
                    # 在没有将句子添加于预定摘要句子集合时，计算MMR
                    # 公式是：alpha * 句子的分数 - （1-alpha） * 句子和摘要集合的分数
                    mmr[sentence] = alpha * scores[sentence] - (1-alpha) * self.cal_sim(sentence, summary)
            # 选择MMR分数最大的句子，留在summary集合中
            try:
                selected = max(mmr.items(), key=operator.itemgetter(1))[0]
            except:
                return []
            summary.append(selected)
            # 继续迭代，直到摘要句子数量满足要求停止
            n -= 1

        intro = [origin_sen_dict[k].lstrip(' ') for k in summary] # 将summary中的句子还原为原始句

        intro_ordered = [i[0] for i in sen_order if i[0] in intro] # 将集合中的句序还原为原文语序
        return intro_ordered

    def update_keyvalue(self, ObId, keyname, value):
        self.db.NEWS.update({"_id":ObjectId(ObId)},{"$set":{keyname:value}},True,True)
        print('Object {} is updated with key:{} and value:{}'.format(ObId, keyname, value))

    def add_summary(self):
        news = self.db.NEWS.find({"$and":[{"coll_date":self.t[-1]},{"intro":{"$exists":True}},{"content":{"$exists":True}}]})
        for doc in news:
            intro = doc["intro"]
            content = doc["content"]
            newsId = doc["_id"]
            if intro == "":
                if content != 'None' or content != [] or content != "" or content != None:
                    summary = content[0:300]
                    self.update_keyvalue(newsId,'intro',summary)