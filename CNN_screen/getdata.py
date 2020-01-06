from pymongo import MongoClient
import argparse
import os
import re

#database-related
parser = argparse.ArgumentParser(description='Get Data from MongoDB database')
parser.add_argument('-overwrite', default=True, help='overwrite existing files if they share the same name')
parser.add_argument('-host', type=str, default='120.27.6.18', help='database host[defalt: 120.**.*.18]')
parser.add_argument('-port', type=str, default='20815', help='database port[default: 20815]')
parser.add_argument('-username', type=str, default='user1', help='database username[default: u****]')
parser.add_argument('-password', type=str, default='user199008', help='database password[default: **********]')
parser.add_argument('-dbname', type=str, default='NEWS', help='database name[default: NEWS]')
parser.add_argument('-collection',type=str,default = 'NEWS')

#jieba-related
parser.add_argument('-dict', type=str, default='./References/dict.txt', help='dictionary for jieba[default: "dict.txt"]')
parser.add_argument('-stop', type=str, default='./References/stop.txt', help='stop words list[default: "stop.txt"]')

#train_test_data related
parser.add_argument('-ratio',type=int,default=3, help='pos_neg train data ratio[default: 0.3]')
args = parser.parse_args()

uri = 'mongodb://' + args.username + ':' + args.password + '@' + args.host + ':' + args.port + '/' + args.dbname
client = MongoClient(uri)
db = client[args.dbname]

print("\nParameters:")
for attr, value in sorted(args.__dict__.items()):
    print("\t{}={}".format(attr.upper(), value))

from dateutil import parser
import datetime

def str2time(testdate):
    datetime_struct = parser.parse(testdate)
    return datetime_struct

def define_dates(time):
    start_date_true_time = time + datetime.timedelta(days=-300)
    start_date_false_time = time + datetime.timedelta(days=-10)
    end_date_time = time + datetime.timedelta(days=-1)
    start_date_true = str(start_date_true_time)[:10]
    start_date_false = str(start_date_false_time)[:10]
    end_date = str(end_date_time)[:10]
    return start_date_true, start_date_false, end_date

class data_collect(object):
    def __init__(self):
       pass

    def getdata(self,testdate):
        textT = []
        textF = []
        textTest = []
        textID = []

        startdate_true, startdate_false, enddate = define_dates(str2time(testdate))


        newsTN = db[args.collection].find({"collect": True}).count()
        newsFN = db[args.collection].find({"collect": False}).count()
        print('There are {} collected and {} uncollected news'.format(newsTN, newsFN))
        print('Data will be collected by:'
              '\nstart_date_for_positive:{}'
              '\nstart_date_for_negative:{}'
              '\nend_date_for_both:{}'
              '\ntest_date:{}'.format(startdate_true, startdate_false, enddate, testdate))
        print('Now preparing data...')

        newsT = db[args.dbname].find(
            {'$and': [{'collect': True}, {"coll_date": {'$gte': startdate_true}}, {"coll_date": {'$lte': enddate}},{"class":"web"}]})
        for doc in newsT:
            try:
                doc["sim_news"]
            except:
                try:
                    doc["intro"]
                    textT.append(doc["title"])
                    textT.append(doc["title"])
                    # textT.append(doc["title"])
                except:
                    textT.append(doc["title"])

        newsF = db[args.dbname].find(
            {'$and': [{'collect': False}, {"coll_date": {'$gte': startdate_false}}, {"coll_date": {'$lte': enddate}},{"class":"web"}]})
        for doc in newsF:
            try:
                doc["sim_news"]
            except:
                textF.append(doc["title"])
        print(len(textT))
        num_neg = len(textF)
        print(num_neg)
        num_pos = args.ratio*num_neg
        print(num_pos)
        print(len(textT[:num_pos]))

        newsTest = db[args.dbname].find({'$and': [{"coll_date": testdate},{"class":"web"}]})
        for doc in newsTest:
            try:
                doc["sim_news"]
            except:
                try:
                    doc["alg1_collect"]
                except:
                    textTest.append(doc["title"])
                    textID.append(doc["_id"])

        print('file_name/data_size:' +
              '\ncollect_file for training:{}, '
              '\nuncollect_file for training:{},'
              '\ncollect_file for test:{}'
              .format(len(textT),len(textF),len(textTest)))

        return(textT,textF,textTest,textID)

if __name__ == "__main__":
    D = data_collect()
    D.getdata('')