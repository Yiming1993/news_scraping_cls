#coding = 'utf-8'

from pymongo import MongoClient
import datetime

class Summary(object):
    def __init__(self):
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name]
        # self.today = str(datetime.datetime.now())[:10]
        self.today = ''

    # def emoji(self):
    #     zuo = chr(0x1F448)
    #     you = chr(0x1F449)
    #     re


    def generate_summary(self):
        news_headline = self.db.NEWS.find({"$and":[{"coll_date":self.today},
                                                   {"intro":{"$exists":True}}]})
        f = open('../Report/summary.txt','w')
        f.write('今日AI数据头条：' + '\n')
        f.close()
        for i in news_headline:
            title = i["title"]
            source = i["source"]
            f = open('../Report/summary.txt','a')
            line = ">" + source + "|" + title + '\n'
            f.write(line)
            f.close()
        f = open('../Report/summary.txt', 'a')
        f.write('\n')
        f.write('' + '\n')
        f.write('👉👈')
        f.close()

if __name__ == '__main__':
    S = Summary()
    S.generate_summary()
