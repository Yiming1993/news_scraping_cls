import jieba
import jieba.analyse
import matplotlib.pyplot as plt
import numpy as np
from pylab import *
#coding='utf-8'
from pymongo import MongoClient
import random
import re
from dateutil import parser as Parser
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
import datetime
import os
import argparse
import random
from bson import ObjectId
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

parser = argparse.ArgumentParser(description='for training and testing')
parser.add_argument('-topK', type = int, default=100)
parser.add_argument('-language',type = str, default= 'Chinese')
parser.add_argument('-type',type = str, default= 'TF_IDF')
parser.add_argument('-days',type=int,default=7)
parser.add_argument('-duplicate',type=bool,default=True)
parser.add_argument('-pos_neg_ratio',type=float,default=1.0)
args = parser.parse_args()

def str2time(testdate):
    datetime_struct = Parser.parse(testdate)
    return datetime_struct

def define_dates(time):
    start_date_true_time = time + datetime.timedelta(days=-300)
    start_date_false_time = time + datetime.timedelta(days=-args.days)
    end_date_time = time + datetime.timedelta(days=-1)
    start_date_true = str(start_date_true_time)[:10]
    start_date_false = str(start_date_false_time)[:10]
    end_date = str(end_date_time)[:10]
    return start_date_true, start_date_false, end_date


class SVM_screen(object):
    def __init__(self):
        self.db_name = ''
        self.host = ''
        self.port = ''
        self.user_name = ''
        self.pass_word = ''
        self.url = 'mongodb://' + self.user_name + ':' + self.pass_word + '@' + self.host + ':' + self.port + '/' + self.db_name
        self.client = MongoClient(self.url)
        self.db = self.client[self.db_name]
        self.ch_list = ['36氪', '新浪科技', '网易智能', '亿欧', '雷锋网', '36Kr', '网易科技']
        self.test_date = str(datetime.datetime.now())[:10]
        print(self.test_date)
        self.start_date_pos, self.start_date_neg, self.end_date_both = define_dates(str2time(self.test_date))
        self.pos_neg_ratio = args.pos_neg_ratio
        self.numbers = ['0','1','2','3','4','5','6','7','8','9',
                        '一','二','三','四','五','六','七','八','九','十',
                        '百','千','万','亿','兆']

    def request_response(self,language ="Chinese",duplicate=True):
        pre_data_pos_title = []
        pre_data_pos_result = []
        pre_data_neg_title = []
        pre_data_neg_result = []
        self.data_language = language
        print("Now collecting data in %s news" % str(self.data_language))
        if language == "Chinese":
            news_train_pos = self.db.NEWS.find({"$and":[{"class": "web"},{"coll_date":{'$gte': self.start_date_pos}},
                                                        {"coll_date":{'$lte': self.end_date_both}},
                                                        {"collect":True}]})
            for doc in news_train_pos:
                if doc["source"] in self.ch_list:
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)
                        if duplicate == True:
                            try:
                                intro = doc["intro"]
                                pre_data_pos_title.append(title)
                                pre_data_pos_result.append(result)
                            except:
                                pass

            pre_data_pos = list(zip(pre_data_pos_title,pre_data_pos_result))
            self.pos_train_num = len(pre_data_pos)
            #print(pre_data_pos)

            train_size = int(len(pre_data_pos) * self.pos_neg_ratio)

            news_train_neg = self.db.NEWS.find({"$and":[{"class": "web"},{"coll_date":{'$gte': self.start_date_neg}},
                                                        {"coll_date":{'$lte': self.end_date_both}},
                                                        {"collect":False}]})
            for doc in news_train_neg:
                if doc["source"] in self.ch_list:
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 0
                        pre_data_neg_title.append(title)
                        pre_data_neg_result.append(result)

            pre_data_neg = list(zip(pre_data_neg_title,pre_data_neg_result))


            random.shuffle(pre_data_neg)
            data_neg = pre_data_neg
            pre_data_pos.extend(data_neg)
            self.neg_train_num = len(data_neg)
            data_list = pre_data_pos

        else:
            news_train_pos = self.db.NEWS.find({"$and": [{"class": "web"}, {"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"collect": True}]})
            for doc in news_train_pos:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)
                        if duplicate == True:
                            try:
                                intro = doc["intro"]
                                pre_data_pos_title.append(title)
                                pre_data_pos_result.append(result)
                            except:
                                pass

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))

            train_size = int(len(pre_data_pos) * self.pos_neg_ratio)

            news_train_neg = self.db.NEWS.find({"$and": [{"class": "web"}, {"coll_date": {'$gte': self.start_date_neg}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"collect": False}]})
            for doc in news_train_neg:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 0
                        pre_data_neg_title.append(title)
                        pre_data_neg_result.append(result)

            pre_data_neg = list(zip(pre_data_neg_title, pre_data_neg_result))

            random.shuffle(pre_data_neg)
            data_neg = pre_data_neg
            pre_data_pos.extend(data_neg)
            data_list = pre_data_pos
            # print(data_list)
        return data_list

    def get_test_data(self,language='Chinese'):
        test_data_title = []
        test_data_id = []
        if language == 'Chinese':
            news_test = self.db.NEWS.find({"$and": [{"class": "web"},
                                                    {"coll_date": self.test_date}]})
            for doc in news_test:
                if doc["source"] in self.ch_list:
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        test_data_title.append(title)
                        test_data_id.append(doc["_id"])

            test_data_list = list(zip(test_data_title, test_data_id))
        else:
            news_test = self.db.NEWS.find(
                {"$and": [{"class": "web"}, {"coll_date": self.test_date}]})

            for doc in news_test:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        test_data_title.append(title)
                        test_data_id.append(doc["_id"])

            test_data_list = list(zip(test_data_title, test_data_id))

        return test_data_list

    def get_vocab(self, language='Chinese'):
        pre_data_pos_title = []
        pre_data_pos_result = []
        print("Now collecting data in %s features" % str(language))
        if language == "Chinese":
            news_train_pos = self.db.NEWS.find({"$and": [{"class": "web"}, {"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}}]})
            for doc in news_train_pos:
                if doc["source"] in self.ch_list:
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))
            # print(pre_data_pos)

            data_list = pre_data_pos

        else:
            news_train_pos = self.db.NEWS.find({"$and": [{"class": "web"}, {"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}}]})
            for doc in news_train_pos:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    try:
                        doc["sim"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))
            # print(pre_data_pos)

            data_list = pre_data_pos

        return data_list

    def save_data(self,data_list,test_data_list):
        if self.data_language == "Chinese":
            for i in data_list:
                f = open('Data_Ch_train.txt','a')
                f.write(str(i)+'\n')
                f.close()

            for m in test_data_list:
                f = open('Data_Ch_test.txt','a')
                f.write(str(m) + '\n')
                f.close()

        elif self.data_language == "English":
            for i in data_list:
                f = open('Data_En_train.txt','a')
                f.write(str(i)+'\n')
                f.close()

            for m in test_data_list:
                f = open('Data_En_test.txt','a')
                f.write(str(m) + '\n')
                f.close()

        print("Data is saved")

    def cutword(self, sentence):
        jieba.load_userdict('./References/dict.txt')
        stopwords = [line.strip() for line in open('./References/stop.txt', 'r', encoding='utf-8').readlines()]
        sentence_seged = jieba.cut((sentence).strip())
        outstr = ''
        for word in sentence_seged:
            if word not in stopwords:
                if word != '\t':
                    if word != '':
                        if word != ' ':
                            if word != '\xa0':
                                if len(word) > 1:
                                    outstr += word
                                    outstr += ','
        outstr = outstr.split(',')
        return outstr

    def TF(self, seged_sentence, topK=100, withWeight=False):
        word = []
        counterColl = {}
        f = open('./References/stop.txt','r').readlines()
        stop = [re.sub(r'\n','',str(i)) for i in f]
        for w in seged_sentence:
            if w != ' ':
                if w != '':
                    if len(w) > 1:
                        if w not in stop:
                            if list(set(w).intersection(set(self.numbers))) == []:
                                if not w in word:
                                    word.append(w)
                                if not w in counterColl:
                                    counterColl[w] = 0
                                else:
                                    counterColl[w] += 1

        coll_list = sorted(counterColl.items(), key=lambda x: x[1], reverse=True)
        if withWeight == True:
            return coll_list[:topK]
        else:
            return [i[0] for i in coll_list][:topK]

    def TF_IDF_en(self,data,topK=100,withWeight=False):
        TF_IDF_dict = {}
        f = open('./References/stop.txt', 'r').readlines()
        stop = [re.sub(r'\n', '', str(i)) for i in f]
        tfidf_vec = TfidfVectorizer()
        tfidf_matrix = tfidf_vec.fit_transform([data])
        words = tfidf_vec.get_feature_names()
        weights = tfidf_matrix.toarray()
        for i in range(len(weights)):
            for j in range(len(words)):
                if words[j] != '':
                    if len(str(words[j])) > 1:
                        if words[j] not in stop:
                            TF_IDF_dict[str(words[j])] = weights[i][j]
        final_list = sorted(TF_IDF_dict.items(),key=lambda x:x[1],reverse=True)
        if withWeight == True:
            return final_list[:topK]
        else:
            return [i[0] for i in final_list][:topK]

    def TF_IDF(self, data, topK=100,withWeight=False,language='Chinese'):
        sentence = ''
        if language == 'Chinese':
            for i in data:
                sentence += i
            return jieba.analyse.extract_tags(sentence,topK=topK, withWeight=withWeight)
        else:
            return self.TF_IDF_en(data,topK=topK, withWeight=withWeight)

    def feature_extraction(self, type="TF_IDF", topK = 100, withWeight=False, language='Chinese'):
        vocab = self.get_vocab(language=language)
        if language == 'Chinese':
            seg_sentence = []
            [seg_sentence.extend(self.cutword(i[0])) for i in vocab]
        else:
            seg_sentence = ''
            for i in vocab:
                seg_sentence += i[0]

        if type == 'TF_IDF':
            self.mainlist = self.TF_IDF(seg_sentence, topK=topK, withWeight=withWeight,language=language)
        else:
            self.mainlist = self.TF_IDF_en(seg_sentence, topK=topK, withWeight=withWeight,language=language)

        return self.mainlist

    def word2vec(self, sentence, mainlist, language='Chinese'):
        if language == 'Chinese':
            seg_sentence = self.cutword(sentence)
            pre_vec = [seg_sentence.count(i) for i in mainlist]
        else:
            pre_vec = [sentence.count(i) for i in mainlist]
        return pre_vec

    def data_preprocessing(self, mainlist, language = 'Chinese', duplicate = True):
        self.raw_data_train = self.request_response(language=language, duplicate=duplicate)
        self.x_train = [self.word2vec(i[0],mainlist,language=language) for i in self.raw_data_train]
        self.y_train = [i[1] for i in self.raw_data_train]

        return self.x_train,self.y_train

    def data_preprocessing_test(self,mainlist,language = 'Chinese'):
        self.raw_data_test = self.get_test_data(language=language)
        self.x_test = [self.word2vec(i[0], mainlist,language=language) for i in self.raw_data_test]
        self.y_id = [i[1] for i in self.raw_data_test]
        return self.x_test,self.y_id

    def SVM_train(self,x_train,y_train):
        clf = SVC(kernel='rbf',C=0.5,probability=True)
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        clf.fit(x_train,y_train)
        return clf

    def SVM_predict(self,clf,x_test):
        x_test = np.array(x_test)
        predict = clf.predict(x_test)
        # print(predict)
        return predict

    def SVM_screen(self,newsId,result):
        # print(str(newsId) + 'is ' + str(result))
        # screened = []
        if result == 0:
            # print(str(newsId) + ' screen: ' + str(result))
            self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"alg2_collect": False}}, True, True)
            self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"screen": True}}, True, True)
        else:
            self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"alg2_collect": True}}, True, True)
    
    def SVM_random(self,random_num=25):
        news = self.db.NEWS.find({"$and":[{"coll_date":self.test_date},{"alg2_collect":False},{"sim_news":{"$exists":False}},{"screen":True}]})
        newsId = [doc["_id"] for doc in news]
        random.shuffle(newsId)
        if len(newsId) >= random_num:
            newsId = newsId[:random_num]
        else:
            pass
        return newsId

    def SVM_intervention(self,newsId):
        news = self.db.NEWS.find({"_id":ObjectId(newsId)})
        for doc in news:
            if doc["screen"] == True:
                self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"screen": False}}, True, True)
            else:
                pass

    def save_model(self,clf,language='Chinese'):
        if language == 'Chinese':
            joblib.dump(clf,"./SVM_SCREEN/train_model_cn.m")
        else:
            joblib.dump(clf,'./SVM_SCREEN/train_model_en.m')
        print('SVM model is saved')

    def save_features(self,mainlist,language='Chinese'):
        if language == 'Chinese':
            for i in mainlist:
                f = open('./SVM_SCREEN/mainlist_cn.txt','a')
                f.write(str(i)+'\n')
                f.close()
        else:
            for i in mainlist:
                f = open('./SVM_SCREEN/mainlist_en.txt','a')
                f.write(str(i)+'\n')
                f.close()

    def reload_features(self,mainlist):
        outlist = [re.sub(r'\n','',str(i)) for i in mainlist]
        return outlist

    def run(self):
        if os.path.isfile('./SVM_SCREEN/train_model_cn.m') == True:
            os.remove('./SVM_SCREEN/train_model_cn.m')
        if os.path.isfile('./SVM_SCREEN/train_model_en.m') == True:
            os.remove('./SVM_SCREEN/train_model_en.m')
        if os.path.isfile('./SVM_SCREEN/mainlist_cn.txt') == True:
            os.remove('./SVM_SCREEN/mainlist_cn.txt')
        if os.path.isfile('./SVM_SCREEN/mainlist_en.txt') == True:
            os.remove('./SVM_SCREEN/mainlist_en.txt')
        self.mainlist_cn = self.feature_extraction(type='TF_IDF', topK=100, language='Chinese')
        x_train, y_train= self.data_preprocessing(self.mainlist_cn, language='Chinese')
        clf_cn = self.SVM_train(x_train, y_train)
        self.save_model(clf_cn,language='Chinese')
        self.save_features(self.mainlist_cn,language='Chinese')
        print('Chinese model is saved')
        self.mainlist_en = self.feature_extraction(type='TF_IDF', topK=100, language='English')
        x_train, y_train = self.data_preprocessing(self.mainlist_en, language='English')
        clf_en = self.SVM_train(x_train, y_train)
        self.save_model(clf_en,language='English')
        self.save_features(self.mainlist_en, language='English')
        print('English model is saved')
    
    def open_model(self,language='Chinese'):
        if language == 'Chinese':
            self.SVM_model = joblib.load("./SVM_SCREEN/train_model_cn.m")
        else:
            self.SVM_model = joblib.load("./SVM_SCREEN/train_model_en.m")
        return self.SVM_model

    def run_test(self):
        self.mainlist_cn = self.reload_features(open('./SVM_SCREEN/mainlist_cn.txt','r').readlines())
        print(self.mainlist_cn)
        x_test,y_id = self.data_preprocessing_test(self.mainlist_cn,language='Chinese')
        model_cn = self.open_model(language='Chinese')
        prediction = self.SVM_predict(model_cn,x_test)
        prediction_list = list(zip(y_id,prediction))
        for i in prediction_list:
            self.SVM_screen(i[0],i[1])
        print('Chinese News is screened')
        self.mainlist_en = self.reload_features(open('./SVM_SCREEN/mainlist_en.txt','r').readlines())
        print(self.mainlist_en)
        x_test, y_id = self.data_preprocessing_test(self.mainlist_en, language='English')
        model_en = self.open_model(language='English')
        prediction = self.SVM_predict(model_en, x_test)
        prediction_list = list(zip(y_id, prediction))
        for i in prediction_list:
            self.SVM_screen(i[0], i[1])
        print('English News is screened')
        newsId = self.SVM_random()
        for i in newsId:
            self.SVM_intervention(i)
        print('Random news is modified')
