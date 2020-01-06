# coding=utf-8
from pymongo import MongoClient
from dateutil import parser
import datetime
# from SVM_classification import feature_extraction
# from news_classification import time
# from LSTM_CNN import time1

host = ''
port = ''
user_name = ''
user_pwd = ''
db_name = ''
uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
client = MongoClient(uri)
db = client[db_name]

def str2time(testdate):
    datetime_struct = parser.parse(testdate)
    return datetime_struct

def daily_report():
    today = str(datetime.datetime.now())[:10]
    yesterday = str(str2time(today) + datetime.timedelta(days=-1))[:10]

    # total number of selected news
    total = db.NEWS.find({'$and': [{'collect':True}, {'coll_date':yesterday}]}).count()

    # selected news from wechat
    source_wechat = []
    count_wechat = []
    total_wechat = 0
    source = db.NEWS.find({'$and': [{"class":"wechat"}, {'coll_date':yesterday}]})
    dict = [doc for doc in source]
    for i in dict:
         if i["source"] not in source_wechat:
              count1 = db.NEWS.find({'$and': [{'source': i["source"]}, {'class':"wechat"}, {'collect':True}, {'coll_date':yesterday}]}).count()
              if count1 > 0:
                   total_wechat += count1
                   source_wechat.append(i["source"])
                   count_wechat.append(count1)
         else:
              pass
    List = list(zip(source_wechat, count_wechat))
    list_wechat = sorted(List, key=lambda x: x[1], reverse=True)

    # selected news from web
    source_web = []
    count_web = []
    source = db.NEWS.find({'$and': [{"class":"web"}, {'coll_date':yesterday}]})
    dict = [doc for doc in source]
    for i in dict:
         if i["source"] not in source_web:
              count2 = db.NEWS.find({'$and': [{'source': i["source"]}, {'class':"web"}, {'collect':True}, {'coll_date':yesterday}]}).count()
              if count2 > 0:
                   source_web.append(i["source"])
                   count_web.append(count2)
         else:
              pass
    List = list(zip(source_web, count_web))
    list_web = sorted(List, key=lambda x: x[1], reverse=True)

    # news from web
    source_pool = []
    t, s = [], []
    source = db.NEWS.find({'$and': [{"class":"web"}, {'coll_date':yesterday}]})
    dict = [doc for doc in source]
    for i in dict:
         if i["source"] not in source_pool:
              source_pool.append(i["source"])
              total_web = db.NEWS.find({'$and': [{'source': i["source"]}, {'class': "web"}, {'coll_date': yesterday}]}).count()
              select_web = db.NEWS.find({'$and': [{'source': i["source"]}, {'class':"web"}, {'collect':True}, {'coll_date':yesterday}]}).count()
              t.append(total_web)
              s.append(select_web)
         else:
              pass
    List = list(zip(source_pool, t))
    List = list(zip(List, s))
    List = sorted(List, key=lambda x: x[1], reverse=True)

    # headline
    headline = db.NEWS.find({"$and": [{"intro":{"$exists":True}}, {"coll_date":yesterday}]})
    head = []
    for i in headline:
         head.append(i['source'])

    # number of login

    # number of clicks
    clicks = db.NEWS.find({"$and": [{"clicks":{"$exists":True}}, {"coll_date":yesterday}]}).count()

    return yesterday, total, total_wechat, list_wechat, list_web, List, head, clicks

if __name__ == "__main__":
    testdate, total, total_wechat, list_wechat, list_web, List, head, clicks = daily_report()
    print("Testdate:", testdate)
    print("Total number of selected news:", total)
    print(list_wechat + list_web)
    print('\n')

    print("Total number of selected news from wechat:", total_wechat)
    print(list_wechat)
    print('\n')

    print("Total and selected number of news from web:")
    print(List)
    print('\n')

    print("The headline is selected from:")
    print(head)
    print('\n')
    print("Clicks of yesterday:", clicks)

    # # SVM performance
    # index = ['TP', 'TN', 'FP', 'FN', 'Accuracy', 'Precision', 'Recall', 'F1_score']
    # result_svm = feature_extraction.run()
    # SVM_performance = list(zip(index, result_svm))
    #
    # # CNN performance
    # result_cnn = time.run()
    # CNN_performance = list(zip(index, result_cnn))
    #
    # # LSTM_CNN performance
    # result_lstm_cnn = time1.run()
    # LSTM_CNN_performance = list(zip(index, result_lstm_cnn))
    #
    # # save
    # db.DAILY_LOG_1.drop()
    # db.DAILY_LOG_1.insert({"test_date": testdate,
    #                        "total_news": total,
    #                        "total_wechat": total_wechat,
    #                        "news_source": list_wechat + list_web,
    #                        "wechat_source": list_wechat,
    #                        "web_source": List,
    #                        "head_source": head,
    #                        "clicks": clicks,
    #                        "SVM_performance":SVM_performance,
    #                        "CNN_performance": CNN_performance,
    #                        "LSTM_CNN_performance": LSTM_CNN_performance})
    # print('Daily report is exported')