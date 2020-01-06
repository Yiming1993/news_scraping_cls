import numpy as np
from SVM_SCREEN.SVM_screen import SVM_screen
import os
import random
from dateutil import parser as Parser
import datetime
from sklearn.externals import joblib
from bson import ObjectId

def str2time(testdate):
    datetime_struct = Parser.parse(testdate)
    return datetime_struct

def define_dates(time):
    start_date_true_time = time + datetime.timedelta(days=-1000)
    start_date_false_time = time + datetime.timedelta(days=-7)
    end_date_time = time + datetime.timedelta(days=-1)
    start_date_true = str(start_date_true_time)[:10]
    start_date_false = str(start_date_false_time)[:10]
    end_date = str(end_date_time)[:10]
    return start_date_true, start_date_false, end_date

class SVM_headline(SVM_screen):
    def __init__(self):
        super(SVM_headline,self).__init__()

    def request_response(self,language ="Chinese",duplicate=True):
        pre_data_pos_title = []
        pre_data_pos_result = []
        pre_data_neg_title = []
        pre_data_neg_result = []
        self.data_language = language
        print("Now collecting data in %s news" % str(self.data_language))
        if language == "Chinese":
            news_train_pos = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"intro":{"$exists":True}}]})
            for doc in news_train_pos:
                if doc["source"] in self.ch_list or doc["class"] == "wechat":
                    title = doc["title"]
                    result = 1
                    pre_data_pos_title.append(title)
                    pre_data_pos_result.append(result)
                    if duplicate == True:
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)


            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))
            self.pos_train_num = len(pre_data_pos)
            # print(pre_data_pos)

            train_size = int(len(pre_data_pos) * self.pos_neg_ratio)

            news_train_neg = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_neg}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"collect": True},{"intro":{"$exists":False}}]})
            for doc in news_train_neg:
                if doc["source"] in self.ch_list or doc["class"] == "wechat":
                    title = doc["title"]
                    result = 0
                    pre_data_neg_title.append(title)
                    pre_data_neg_result.append(result)

            pre_data_neg = list(zip(pre_data_neg_title, pre_data_neg_result))

            random.shuffle(pre_data_neg)
            data_neg = pre_data_neg
            pre_data_pos.extend(data_neg)
            self.neg_train_num = len(data_neg)
            data_list = pre_data_pos

        else:
            news_train_pos = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"intro":{"$exists":True}}]})
            for doc in news_train_pos:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    title = doc["title"]
                    result = 1
                    pre_data_pos_title.append(title)
                    pre_data_pos_result.append(result)
                    if duplicate == True:
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))

            train_size = int(len(pre_data_pos) * self.pos_neg_ratio)

            news_train_neg = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_neg}},
                                                         {"coll_date": {'$lte': self.end_date_both}},
                                                         {"collect":True},{"intro":{"$exists":False}}]})
            for doc in news_train_neg:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
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
        self.train_pos = len(pre_data_pos)
        self.train_neg = len(pre_data_neg)
        return data_list

    def get_test_data(self,language='Chinese'):
        test_data_title = []
        test_data_id = []
        if language == 'Chinese':
            news_test = self.db.NEWS.find({"coll_date": self.test_date})

            for doc in news_test:
                if doc["source"] in self.ch_list:
                    title = doc["title"]
                    test_data_title.append(title)
                    test_data_id.append(doc["_id"])
                elif doc["class"] == "wechat":
                    title = doc["title"]
                    test_data_title.append(title)
                    test_data_id.append(doc["_id"])

            test_data_list = list(zip(test_data_title, test_data_id))
        else:
            news_test = self.db.NEWS.find(
                {"coll_date": self.test_date})

            for doc in news_test:
                if doc["source"] not in self.ch_list:
                    if doc["class"] != 'wechat':
                        title = doc["title"]
                        test_data_title.append(title)
                        test_data_id.append(doc["_id"])

            test_data_list = list(zip(test_data_title, test_data_id))
        self.test_size = len(test_data_list)
        return test_data_list

    def get_vocab(self, language='Chinese'):
        pre_data_pos_title = []
        pre_data_pos_result = []
        print("Now collecting data in %s features" % str(language))
        if language == "Chinese":
            news_train_pos = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}},{"collect":True}]})
            for doc in news_train_pos:
                if doc["source"] in self.ch_list or doc["class"] == "wechat":
                    try:
                        doc["sim_news"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))
            # print(pre_data_pos)

            data_list = pre_data_pos

        else:
            news_train_pos = self.db.NEWS.find({"$and": [{"coll_date": {'$gte': self.start_date_pos}},
                                                         {"coll_date": {'$lte': self.end_date_both}},{"collect":True}]})
            for doc in news_train_pos:
                if doc["source"] not in self.ch_list and doc["class"] != 'wechat':
                    try:
                        doc["sim_news"]
                    except:
                        title = doc["title"]
                        result = 1
                        pre_data_pos_title.append(title)
                        pre_data_pos_result.append(result)

            pre_data_pos = list(zip(pre_data_pos_title, pre_data_pos_result))
            # print(pre_data_pos)

            data_list = pre_data_pos
        return data_list

    def data_preprocessing_test(self,mainlist,language = 'Chinese'):
        self.raw_data_test = self.get_test_data(language=language)
        self.x_test = [self.word2vec(i[0], mainlist, language=language) for i in self.raw_data_test]
        self.y_id = [i[1] for i in self.raw_data_test]
        self.x_title = [i[0] for i in self.raw_data_test]
        return self.x_test,self.x_title, self.y_id

    def SVM_headline(self,clf,x_test):
        x_test = np.array(x_test)
        proba = clf.predict_proba(x_test)
        return proba.tolist()

    def SVM_orderer(self,x_test,proba):
        if x_test != []:
            proba_list = {}
            proba = [i[1] for i in proba]
            proba_list_pre = list(zip(x_test,proba))
            for i in proba_list_pre:
                proba_list[str(i[0])] = i[1]
            proba_list_final = sorted(proba_list.items(), key=lambda x: x[1], reverse=True)
            return proba_list_final
        else:
            print('today has no news to be recommended')
            return []

    def Headline_check(self):
        news = self.db.NEWS.find({"$and":[{"coll_date":self.test_date},{"intro":{"$exists":True}}]})
        news_title = [doc["title"] for doc in news]
        return news_title

    def save_model(self,clf,language='Chinese'):
        if language == 'Chinese':
            joblib.dump(clf,"./SVM_HEADLINE/train_headline_cn.m")
        else:
            joblib.dump(clf,'./SVM_HEADLINE/train_headline_en.m')
        print('SVM model is saved')

    def save_features(self,mainlist,language='Chinese'):
        if language == 'Chinese':
            for i in mainlist:
                f = open('./SVM_HEADLINE/headlinelist_cn.txt','a')
                f.write(str(i)+'\n')
                f.close()
        else:
            for i in mainlist:
                f = open('./SVM_HEADLINE/headlinelist_en.txt','a')
                f.write(str(i)+'\n')
                f.close()

    def open_model(self,language='Chinese'):
        if language == 'Chinese':
            self.SVM_model = joblib.load("./SVM_HEADLINE/train_headline_cn.m")
        else:
            self.SVM_model = joblib.load("./SVM_HEADLINE/train_headline_en.m")
        return self.SVM_model

    def get_check_data(self,language='Chinese'):
        test_data_title = []
        test_data_id = []
        news_test = self.db.NEWS.find({"$and": [{"coll_date": self.test_date},
                                                {"intro": {"$exists": True}}]})
        for doc in news_test:
            title = doc["title"]
            test_data_title.append(title)
            test_data_id.append(doc["_id"])

        test_data_list = list(zip(test_data_title, test_data_id))

        return test_data_list

    def intersection_list(self, x, y):
        intersection_list = list(set(x).intersection(set(y)))
        return intersection_list

    def cover_alert(self,date,taglist1,taglist2):
        tag_cover = self.intersection_list(taglist1,taglist2)
        if taglist1 == tag_cover:
            print(str(date)+'\n'+'tag_num to cover all: ' + str(len(taglist2)))
            return 1
        else:
            return 0

    def remove_covered(self,order,wholelist):
        wholelist.pop(order)

    def add_headline_proba(self,proba_list):
        for i in proba_list:
            id = i[0]
            proba = i[1]
            proba = round(proba,5)
            # print(id)
            # print(proba)
            self.db.NEWS.update({"_id": ObjectId(id)}, {'$set': {"hd_alg1": proba}}, True, True)
        print('News is sorted')

    def run(self):
        if os.path.isfile('./SVM_HEADLINE/train_headline_cn.m') == True:
            os.remove('./SVM_HEADLINE/train_headline_cn.m')
        if os.path.isfile('./SVM_HEADLINE/train_headline_en.m') == True:
            os.remove('./SVM_HEADLINE/train_headline_en.m')
        if os.path.isfile('./SVM_HEADLINE/headlinelist_cn.txt') == True:
            os.remove('./SVM_HEADLINE/headlinelist_cn.txt')
        if os.path.isfile('./SVM_HEADLINE/headlinelist_en.txt') == True:
            os.remove('./SVM_HEADLINE/headlinelist_en.txt')
        self.mainlist_cn = self.feature_extraction(type='TF_IDF', topK=100, language='Chinese')
        x_train, y_train = self.data_preprocessing(self.mainlist_cn, language='Chinese')
        clf_cn = self.SVM_train(x_train, y_train)
        self.save_model(clf_cn, language='Chinese')
        self.save_features(self.mainlist_cn, language='Chinese')
        print('Chinese model is saved')
        self.mainlist_en = self.feature_extraction(type='TF_IDF', topK=100, language='English')
        x_train, y_train = self.data_preprocessing(self.mainlist_en, language='English')
        clf_en = self.SVM_train(x_train, y_train)
        self.save_model(clf_en, language='English')
        self.save_features(self.mainlist_en, language='English')
        print('English model is saved')

    def run_headline(self):
        self.mainlist_cn = self.reload_features(open('./SVM_HEADLINE/headlinelist_cn.txt', 'r').readlines())
        # print(self.mainlist_cn)
        x_test, x_title, y_id = self.data_preprocessing_test(self.mainlist_cn, language='Chinese')
        model_cn = self.open_model(language='Chinese')
        proba = self.SVM_headline(model_cn,x_test)
        proba_list_cn = self.SVM_orderer(y_id,proba)
        self.add_headline_proba(proba_list_cn)
        self.mainlist_en = self.reload_features(open('./SVM_HEADLINE/headlinelist_en.txt', 'r').readlines())
        x_test, x_title, y_id = self.data_preprocessing_test(self.mainlist_en, language='English')
        model_cn = self.open_model(language='English')
        proba = self.SVM_headline(model_cn, x_test)
        proba_list_en = self.SVM_orderer(y_id, proba)
        self.add_headline_proba(proba_list_en)