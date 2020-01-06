#coding='utf-8'
from pymongo import MongoClient
from Spider.spider import Spider
import wechatsogou
import re

class Clean_Wechat(Spider):
    def __init__(self):
        super(Clean_Wechat,self).__init__('no','no','no','no')
        self.ws_api = wechatsogou.WechatSogouAPI()

    def get_data(self,start_date,end_date):
        news = self.db.NEWS.find({"$and": [{"collect": True}, {"coll_date": {"$gte": start_date}},
                                           {"coll_date": {"$lte": end_date}}, {"class": "wechat"}]})
        source_list = list(set([i["source"] for i in news]))
        return source_list

    def clean_list(self,source_list,start_date,end_date):
        wechat_list = self.db.NEWS.find({"$and": [{"collect": True}, {"coll_date": {"$gte": start_date}},
                                           {"coll_date": {"$lte": end_date}}, {"class": "wechat"}]})
        keep_list = list(set([i["source"] for i in wechat_list]))
        clean_list = [i for i in source_list if i not in keep_list]
        return clean_list

    def get_wechat_name(self,wechat_account):

        wechat_profile = self.ws_api.get_gzh_info(wechat_account)
        try:
            wechat_name = wechat_profile["wechat_name"]
        except:
            wechat_name = None
        print(wechat_name)
        return wechat_name

if __name__ == "__main__":
    C = Clean_Wechat()
    f = open('./References/wechat_path.txt')
    h_list = [re.sub(r'\n','',str(i)) for i in f]
    wechat_name_list = [C.get_wechat_name(i) for i in h_list]
