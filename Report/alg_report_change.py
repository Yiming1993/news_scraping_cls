import numpy as np
from pymongo import MongoClient
from sklearn.metrics import confusion_matrix
from dateutil import parser
import datetime
from bson import ObjectId
from Report import daily_report

np.set_printoptions(suppress=True)

def str2time(testdate):
    datetime_struct = parser.parse(testdate)
    return datetime_struct

def define_dates(time):
    start_date_true_time = time + datetime.timedelta(days=-300)
    start_date_false_time = time + datetime.timedelta(days=-7)
    end_date_time = time + datetime.timedelta(days=-1)
    start_date_true = str(start_date_true_time)[:10]
    start_date_false = str(start_date_false_time)[:10]
    end_date = str(end_date_time)[:10]
    return start_date_true, start_date_false, end_date

class report_extraction(object):
    def __init__(self):
        username = ''
        password = ''
        dbname = ''
        host = ''
        port = ''
        url = 'mongodb://' + username + ':' + password + '@' + host + ':' + port + '/' + dbname
        client = MongoClient(url)
        self.db = client[dbname]
        self.ch_list = ['36氪', '新浪科技', '网易智能', '亿欧', '雷锋网', '36Kr', '网易科技']

    def date(self):
        today = str(datetime.datetime.now())[:10]
        test_date = str(str2time(today) + datetime.timedelta(days=-1))[:10]
        print(test_date)
        startdate_true, startdate_false, enddate = define_dates(str2time(test_date))
        return test_date,startdate_true, startdate_false, enddate

    def report_making_alg1(self,date,startdate_true,startdate_false,enddate):
        y_test = []
        all_predictions = []
        x_eval = []

        news = self.db.NEWS.find({'$and': [{"coll_date":date}, {"class":"web"}]})
        fail_news = 0
        for doc in news:
            try:
                doc["sim_news"]
            except:
                try:
                    if doc["alg1_collect"] == True:
                        all_predictions.append(1)
                    else:
                        all_predictions.append(0)

                    x_eval.append(doc["title"])
                    if doc["collect"] == True:
                        y_test.append(1)
                    else:
                        y_test.append(0)
                except:
                    fail_news +=1

        print('there are %s news failed to be processed by alg1'% str(fail_news))

        newsT = self.db.NEWS.find(
                    {'$and': [{'collect': True}, {"coll_date": {'$gte': startdate_true}}, {"coll_date": {'$lte': enddate}},{"class":"web"}]})
        textT = 0
        headline_num = 0
        for doc in newsT:
            try:
                sims = doc["sim_news"]
            except:
                try:
                    intro = doc["intro"]
                    textT +=1
                    textT +=1
                    # textT.append(doc["title"])
                except:
                    textT +=1

        textF = 0
        newsF = self.db.NEWS.find(
                    {'$and': [{'collect': False}, {"coll_date": {'$gte': startdate_false}}, {"coll_date": {'$lte': enddate}},{"class":"web"}]})
        for doc in newsF:
            try:
                sims = doc["sim_news"]
            except:
                textF +=1

        test_total = 0
        newsTest = self.db.NEWS.find({'$and': [{"coll_date": date},{"class":"web"}]})
        for doc in newsTest:
            try:
                sims = doc["sim_news"]
            except:
                try:
                    intro = doc["intro"]
                    headline_num +=1
                    test_total +=1
                except:
                    test_total +=1

        if y_test and all_predictions is not None:

            result = confusion_matrix(y_test, all_predictions).ravel().tolist()
            PosP = all_predictions.count(1)
            NegP = all_predictions.count(0)
            PosY = y_test.count(1)
            NegY = y_test.count(0)

            Tn = result[0]
            Fp = result[1]
            Fn = result[2]
            Tp = result[3]

            Tpp = round(Tp / (len(y_test)), 4)
            Fpp = round(Fp / (len(y_test)), 4)
            Tnp = round(Tn / (len(y_test)), 4)
            Fnp = round(Fn / (len(y_test)), 4)

            Accuracy = (Tp + Tn) / (Tp + Tn + Fp + Fn)
            Precision = Tp / (Tp + Fp)
            Recall = Tp / (Tp + Fn)
            Specificity = Tn / (Tn + Fp)
            F1_score = (2*Precision*Recall) / (Precision + Recall)

            print(datetime.datetime.now())
            print(
                'Prediction:\nPositive:{}/Negative:{}\n'
                'Real Value:\nPositive:{}/Negative:{}\n'
                'TP:{}/{} | TN:{}/{} '
                '\nFP:{}/{} | FN:{}/{}'
                '\nTotal number of test examples:{}'
                    .format(PosP, NegP,
                            PosY, NegY,
                            Tp, Tpp,
                            Tn, Tnp,
                            Fp, Fpp,
                            Fn, Fnp,
                            len(y_test)))

            print("Accuracy: {:g}".format(Accuracy))
            print("Precision:{:g}".format(Precision))
            print("Recall:{:g}".format(Recall))
            print("Specificity:{:g}".format(Specificity))

            FalseNegPosition = []
            zipped_result = list(zip(y_test, all_predictions))

            iterT = 0
            for i in zipped_result:
                if i[0] > i[1]:
                    FalseNegPosition.append(iterT)
                iterT += 1

            iterM = 0
            FalseNegTitles = []
            for i in list(x_eval):
                if iterM in FalseNegPosition:
                    FalseNegTitles.append(i)
                iterM += 1

            NonNegHeadlineNum = 0
            NegHeadline = []
            print('False Negative news:' + '\n')
            # f.write('False Negative news:' + '\n')
            if FalseNegTitles == []:
                print('There is no false negative news')
            else:
                for i in FalseNegTitles:
                    print(i)
                    # f.write(str(i)+'\n')
                    FalseNegTitle = self.db.NEWS.find({"title": i})
                    for doc in FalseNegTitle:
                        try:
                            NegHeadIntro = doc["intro"]
                            NegHeadline.append(i)

                        except:
                            NonNegHeadlineNum += 1
                            pass

            NegHeadlineNum = len(NegHeadline)

            if headline_num != 0:
                print("Incorrect headline number:\n%s" % str(NegHeadlineNum) + '\n')
                NegHeadlineRatio = round(NegHeadlineNum / headline_num, 4) * 100
                print(
                    "Incorrect headline ratio:\n%s" % str(NegHeadlineRatio) + '%\n')
            else:
                print("\n")
                print("There is no False Negative headline\n")
                NegHeadlineRatio = 0

            # self.db.ALG1_DAILY_LOG.insert_one({"Test_Date":date,
            #                          "Train_Pos":textT,
            #                          "Train_Neg":textF,
            #                          "Test_Pos":PosY,
            #                          "Test_Neg":NegY,
            #                          "Test_Total":test_total,
            #                          "Pre_Pos":PosP,
            #                          "FN":Fn,
            #                          "FN_Ratio":Fnp,
            #                          "Num_Headline_Total":headline_num,
            #                          "FN_Headline_Num":NegHeadlineNum,
            #                          "FN_Headline_Ratio":NegHeadlineRatio,
            #                          "FN_News":FalseNegTitles,
            #                          "FN_Headlines":NegHeadline})

            print("%s alg1 daily report is exported"% date)
        else:
            print('there is no available data for daily report')

        return Tp, Tn, Fp, Fn, Accuracy, Precision, Recall, Specificity, F1_score

    def report_making_alg2(self, date, startdate_true, startdate_false, enddate):
        y_test = []
        all_predictions = []
        x_eval = []

        news = self.db.NEWS.find({'$and': [{"coll_date": date}, {"class": "web"}]})
        fail_news = 0
        for doc in news:
            try:
                doc["sim_news"]
            except:
                try:
                    if doc["alg2_collect"] == True:
                        all_predictions.append(1)
                    else:
                        all_predictions.append(0)

                    x_eval.append(doc["title"])
                    if doc["collect"] == True:
                        y_test.append(1)
                    else:
                        y_test.append(0)
                except:
                    fail_news += 1

        print('there are %s news failed to be processed by alg2' % str(fail_news))

        newsT = self.db.NEWS.find(
                {'$and': [{'collect': True}, {"coll_date": {'$gte': startdate_true}}, {"coll_date": {'$lte': enddate}},
                          {"class": "web"}]})
        textT = 0
        headline_num = 0
        for doc in newsT:
            try:
                sims = doc["sim_news"]
            except:
                try:
                    intro = doc["intro"]
                    textT += 1
                    textT += 1
                    # textT.append(doc["title"])
                except:
                    textT += 1
        textF = 0
        newsF = self.db.NEWS.find(
                {'$and': [{'collect': False}, {"coll_date": {'$gte': startdate_false}},
                          {"coll_date": {'$lte': enddate}}, {"class": "web"}]})
        for doc in newsF:
            try:
                sims = doc["sim_news"]
            except:
                textF += 1

        test_total = 0
        newsTest = self.db.NEWS.find({'$and': [{"coll_date": date}, {"class": "web"}]})
        for doc in newsTest:
            try:
                sims = doc["sim_news"]
            except:
                try:
                    intro = doc["intro"]
                    headline_num += 1
                    test_total += 1
                except:
                    test_total += 1

        if y_test and all_predictions is not None:
            result = confusion_matrix(y_test, all_predictions).ravel().tolist()
            PosP = all_predictions.count(1)
            NegP = all_predictions.count(0)
            PosY = y_test.count(1)
            NegY = y_test.count(0)

            Tn = result[0]
            Fp = result[1]
            Fn = result[2]
            Tp = result[3]

            Tpp = round(Tp / (len(y_test)), 4)
            Fpp = round(Fp / (len(y_test)), 4)
            Tnp = round(Tn / (len(y_test)), 4)
            Fnp = round(Fn / (len(y_test)), 4)

            Accuracy = (Tp + Tn) / (Tp + Tn + Fp + Fn)
            Precision = Tp / (Tp + Fp)
            Recall = Tp / (Tp + Fn)
            Specificity = Tn / (Tn + Fp)
            F1_score = (2*Precision*Recall) / (Precision + Recall)

            print(datetime.datetime.now())
            print(
                'Prediction:\nPositive:{}/Negative:{}\n'
                'Real Value:\nPositive:{}/Negative:{}\n'
                'TP:{}/{} | TN:{}/{} '
                '\nFP:{}/{} | FN:{}/{}'
                '\nTotal number of test examples:{}'
                    .format(PosP, NegP,
                            PosY, NegY,
                            Tp, Tpp,
                            Tn, Tnp,
                            Fp, Fpp,
                            Fn, Fnp,
                            len(y_test)))

            print("Accuracy: {:g}".format(Accuracy))
            print("Precision:{:g}".format(Precision))
            print("Recall:{:g}".format(Recall))
            print("Specificity:{:g}".format(Specificity))
            FalseNegPosition = []
            zipped_result = list(zip(y_test, all_predictions))

            iterT = 0
            for i in zipped_result:
                if i[0] > i[1]:
                    FalseNegPosition.append(iterT)
                iterT += 1

            iterM = 0
            FalseNegTitles = []
            for i in list(x_eval):
                if iterM in FalseNegPosition:
                    FalseNegTitles.append(i)
                iterM += 1
            NonNegHeadlineNum = 0
            NegHeadline = []
            print('False Negative news:' + '\n')
                # f.write('False Negative news:' + '\n')
            if FalseNegTitles == []:
                print('There is no false negative news')
            else:
                for i in FalseNegTitles:
                    print(i)
                        # f.write(str(i)+'\n')
                    FalseNegTitle = self.db.NEWS.find({"title": i})
                    for doc in FalseNegTitle:
                        try:
                            NegHeadIntro = doc["intro"]
                            NegHeadline.append(i)
                        except:
                            NonNegHeadlineNum += 1
                            pass

            NegHeadlineNum = len(NegHeadline)

            if headline_num != 0:
                print("Incorrect headline number:\n%s" % str(NegHeadlineNum) + '\n')
                NegHeadlineRatio = round(NegHeadlineNum / headline_num, 4) * 100
                print("Incorrect headline ratio:\n%s" % str(NegHeadlineRatio) + '%\n')
            else:
                print("\n")
                print("There is no False Negative headline\n")
                NegHeadlineRatio = 0

            # self.db.ALG2_DAILY_LOG.insert_one({"Test_Date": date,
            #                                        "Train_Pos": textT,
            #                                        "Train_Neg": textF,
            #                                        "Test_Pos": PosY,
            #                                        "Test_Neg": NegY,
            #                                        "Test_Total": test_total,
            #                                        "Pre_Pos": PosP,
            #                                        "FN": Fn,
            #                                        "FN_Ratio": Fnp,
            #                                        "Num_Headline_Total": headline_num,
            #                                        "FN_Headline_Num": NegHeadlineNum,
            #                                        "FN_Headline_Ratio": NegHeadlineRatio,
            #                                        "FN_News": FalseNegTitles,
            #                                        "FN_Headlines": NegHeadline})

            print("%s alg2 daily report is exported" % date)
        else:
            print('there is no available data for daily report')

        return Tp, Tn, Fp, Fn, Accuracy, Precision, Recall, Specificity, F1_score

    def news_count_language(self,date,language='Chinese'):
        if language == 'Chinese':
            news = self.db.NEWS.find({'$and':[{"collect":True},{"coll_date":date}]})
            newsT = [i for i in news if i["source"] in self.ch_list]
            newsF = self.db.NEWS.find({'$and':[{"collect":False},{"coll_date":date}]})
            newsT_num = len(newsT)
            newsFN = [i for i in news if i["alg2_collect"] == False]
            newsFN_num = len(newsFN)
            print(newsT_num, newsFN_num)
        else:
            news = self.db.NEWS.find({'$and': [{"collect": True}, {"coll_date": date}]})
            newsT = [i for i in news if i["source"] not in self.ch_list and i["class"] != 'wehat']
            newsF = self.db.NEWS.find({'$and': [{"collect": False}, {"coll_date": date}]})
            newsT_num = len(newsT)
            newsFN = [i for i in news if i["alg2_collect"] == False]
            newsFN_num = len(newsFN)
            print(newsT_num, newsFN_num)

    def rating(self,result,whole,thredhold=3):
        range_min = thredhold
        range_max = int(whole-thredhold)
        matrix = np.array(result)
        matrix[matrix <= range_min] = whole
        matrix[matrix >= range_max] = 0
        rate = np.mean((whole-matrix)/whole)
        return rate

    def headline_report(self,date):
        y_pred_pre = {}
        cover_list = {}
        news_pred = self.db.NEWS.find({'$and': [{"coll_date": date}, {"hd_score":{"$exists":True}}]})
        for doc in news_pred:
            y_pred_pre[doc["title"]] = doc["hd_score"]
        y_pred_pre = sorted(y_pred_pre.items(), key = lambda x:x[1],reverse=True)
        news_true = self.db.NEWS.find({'$and': [{"coll_date": date}, {"intro":{"$exists":True}}]})
        y_true = [doc["title"] for doc in news_true]
        y_pred = [i[0] for i in y_pred_pre]
        for i in y_true:
            cover_list[i] = y_pred.index(i)
        cover_list = sorted(cover_list.items(),key=lambda x:x[1],reverse=False)
        cover = [i[1] for i in cover_list]
        min_ = np.min(np.array(cover))
        max_ = np.max(np.array(cover))
        full = len(y_pred)
        rate = self.rating(cover,full)
        return min_,max_,full,rate,y_true,y_pred[:3]

    def headline_report_extraction(self,date,min_,max_,whole_len,rate,real_three,pred_three):
        # self.db.HD_ALG1_DAILY_LOG.insert({"date": date,
        #                                 "max": int(max_),
        #                                 "min": int(min_),
        #                                 "whole_len": int(whole_len),
        #                                 "rate": float(rate),
        #                                 "real_hd": real_three,
        #                                 "pred_hd": pred_three})
        print('Headline report is exported')

    def tag_report(self,date,newsId,thredhold=5):
        rate = 0
        # print(newsId)
        news_tag = self.db.NEWS.find({"_id":ObjectId(newsId)})
        dict = [doc for doc in news_tag][0]
        tags1 = dict['alg1_tag_content']
        tags2 = dict['alg1_tag_genre']
        real_ = dict['tag']
        title = dict['title']
        tag_pool_content = self.db.TAGS.find({"$or": [{"class": "tech"}, {"class": "industry"}, {"class": "cross"}]})
        tag_pool_genre = self.db.TAGS.find({"class": "genre"})
        content_ = [i["name"] for i in tag_pool_content]
        genre_ = [i["name"] for i in tag_pool_genre]
        for i in real_:
            if i in content_:
                rate += self.rating(tags1.index(i),len(tags1),thredhold=thredhold)
            elif i in genre_:
                rate += self.rating(tags2.index(i),len(tags2),thredhold=thredhold)
        rate_final = rate/len(real_)
        return rate_final,tags1[:thredhold],tags2[:thredhold],real_,title

    def get_newsId(self,date):
        news = self.db.NEWS.find({"$and":[{"collect":True},{"coll_date":date},{"tag":{"$exists":True}}]})
        return [doc["_id"] for doc in news]

    def tag_report_extraction(self,date,title,tags1,tags2,real_,rate):
        # self.db.ALG1_TAG_DAILY_LOG.insert({"date": date,
        #                                   "title":title,
        #                                   "alg1_tag_content": tags1,
        #                                   "alg1_tag_genre": tags2,
        #                                   "real_tags": real_,
        #                                   "rate": rate})
        print('Tag of %s report is exported' % str(title))

    def tag_daily_summary(self,date,rate,news_list):
        self.db.ALG1_TAG_DAILY_LOG.insert({"date": date,
                                           "average_rate": rate,
                                           "news_num":str(len(news_list))})
        print('Tags daily report is exported')

    def tag_run(self,date):
        rate = 0
        news_list = self.get_newsId(date)
        for i in news_list:
            try:
                rate_,tags1,tags2,real_,title = self.tag_report(date,str(i))
                self.tag_report_extraction(date,title,tags1,tags2,real_,rate_)
                rate += rate_
            except:
                pass
        self.tag_daily_summary(date,rate/len(news_list),news_list)

    def toutiao_count(self,date):
        news_toutiao_pre = self.db.NEWS_toutiao.find({"$and":[{"coll_date":date},{"channel":"toutiao"}]})
        news_wechat_pre = self.db.NEWS.find({"$and":[{"coll_date":date},{"class":"wechat"}]})
        news_toutiao = [doc["title"] for doc in news_toutiao_pre]
        news_wechat = [doc["title"] for doc in news_wechat_pre]
        intersection = list(set(news_wechat).intersection(set(news_toutiao)))
        uncovered_list = []
        for i in news_wechat:
            if i not in intersection:
                uncovered_list.append(i)
        uncovered = len(uncovered_list)
        toutiao_len = len(news_toutiao)
        wechat_len = len(news_wechat)
        covered_ratio = uncovered/(toutiao_len+wechat_len)
        return uncovered,covered_ratio,wechat_len,toutiao_len,uncovered_list

    def toutiao_report(self,date):
        uncovered,covered_ratio,wechat_len,toutiao_len,uncovered_list = self.toutiao_count(date)
        # self.db.TOUTIAO_DAILY_LOG.insert({"date": date,
        #                                    "toutiao_len": toutiao_len,
        #                                    "wechat_len": wechat_len,
        #                                    "covered_ratio": covered_ratio,
        #                                    "uncovered_num": uncovered,
        #                                    "uncovered_list":uncovered_list})
        print('Toutiao report is exported')

    def daily_report(self, testdate, total, total_wechat, list_wechat, list_web, List, head, clicks, dict):
        self.db.DAILY_LOG_1.insert({"test_date": testdate,
                                    "total_news": total,
                                    "total_wechat": total_wechat,
                                    "news_source": list_wechat + list_web,
                                    "wechat_source": list_wechat,
                                    "web_source": List,
                                    "head_source": head,
                                    "clicks": clicks,
                                    "algorithm_performance": dict})
        print('Daily report is exported')

if __name__ == '__main__':
    D = report_extraction()
    date, startdate_true, startdate_false, enddate = D.date()
    # D.news_count_language(date,language='Chinese')
    # D.news_count_language(date,language='English')
    Tp1, Tn1, Fp1, Fn1, Accuracy1, Precision1, Recall1, Specificity1, F1_score1 = D.report_making_alg1(date, startdate_true, startdate_false, enddate)
    Tp2, Tn2, Fp2, Fn2, Accuracy2, Precision2, Recall2, Specificity2, F1_score2 = D.report_making_alg2(date, startdate_true, startdate_false, enddate)
    # D.tag_run(date)
    # from SVM_SCREEN import SVM_screen
    # SVM_screen.SVM_screen().run()
    # from Auto_tag import add_tag
    # add_tag.add_tag().run()
    # from SVM_HEADLINE import SVM_headline
    # SVM_headline.SVM_headline().run()
    min_, max_, full, rate, y_true, y_pred = D.headline_report(date)
    D.headline_report_extraction(date, min_, max_, full, rate, y_true, y_pred)

    dict = {}
    CNN_dict = {'TP':Tp1, 'TN':Tn1, 'FP':Fp1, 'FN':Fn1, 'Accuracy':Accuracy1, 'Precision':Precision1,
                'Recall':Recall1,'Specificity':Specificity1, 'F1_score':F1_score1}
    SVM_dict = {'TP': Tp2, 'TN': Tn2, 'FP': Fp2, 'FN': Fn2, 'Accuracy': Accuracy2, 'Precision': Precision2,
                'Recall': Recall2, 'Specificity': Specificity2, 'F1_score': F1_score2}
    dict['CNN'] = CNN_dict
    dict['SVM'] = SVM_dict

    testdate, total, total_wechat, list_wechat, list_web, List, head, clicks = daily_report.daily_report()
    D.daily_report(testdate, total, total_wechat, list_wechat, list_web, List, head, clicks, dict)