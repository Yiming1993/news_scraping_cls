#coding=UTF-8
# from pymongo import MongoClient
from Spider.spider import Spider
import urllib.request
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import json
# import gzip
# from hashlib import md5
# from pyv8 import PyV8
# import requests
import random
from dateutil import rrule
import datetime

class toutiao(Spider):
    def __init__(self):
        super(toutiao, self).__init__('wechat', "wechat", 'wechat', 'web')
        self.tth_url_1 = "https://www.toutiao.com/c/user/article/?page_type=1&user_id="
        self.tth_url_2 = "&max_behot_time=0&count=20"
        self.usrAgent = ["Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
                         "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
                         "Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
                         "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
                         "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
                         "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
                         "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
                         "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
                         "Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3"]
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.toutiao.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json,text/javascript',
            'Cache-Control': 'no-cache',
            'Accept-Language': 'zh-cn',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': '',
        }
        self.tt_search_url_1 = 'https://www.toutiao.com/search_content/?offset='
        self.tt_search_url_2 = '&format=json&keyword='
        self.tt_search_url_3 = '&autoload=true&count=40&cur_tab=1&from=search_tab'
        # self.ctxt = PyV8.JSContext()
        self.tt_hot_url_1 = 'https://www.toutiao.com/api/pc/media_hot/?media_id='
        self.tth_ID = 'https://www.toutiao.com/c/user/'
        self.items = []
        self.proxy = {}

    def random_select_header(self,list):
        agent = random.choice(list)
        return agent

    def get_ip_list(self,obj):
        ip_text = obj.findAll('tr', {'class': 'odd'})
        ip_list = []
        for i in range(len(ip_text)):
            ip_tag = ip_text[i].findAll('td')
            ip_port = ip_tag[1].get_text() + ':' + ip_tag[2].get_text()
            ip_list.append(ip_port)
        # print("共收集到了{}个代理IP".format(len(ip_list)))
        # print(ip_list)
        return ip_list

    def get_random_ip(self):
        ip_list = self.get_ip_list(self.bsObj)
        random_ip = 'http://' + random.choice(ip_list)
        self.proxy = {'http:': random_ip}
        # print('check point: get_proxy')

    def get_proxy(self):
        '''
        only run once for a day, save a self.bsObjct for proxy pool
        :return:
        '''
        url = 'http://www.xicidaili.com/nn'
        headers = {}
        headers["User-Agent"] = self.random_select_header(self.usrAgent)
        headers["Upgrade-Insecure-Requests"] = 1
        headers["Accept-Language"] = 'zh-cn'
        headers["Connection"] = 'keep-alive'
        headers["Accept"] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        headers["Host"] = 'www.xicidaili.com'
        headers["Referer"] = 'www.xicidaili.com'
        request = urllib.request.Request(url,headers=headers)
        response = urllib.request.urlopen(request)
        self.bsObj = BeautifulSoup(response, 'lxml')

    # def get_tth(self,tthId):
    #     '''
    #     get articles from 头条号
    #     :param tthId:
    #     :return:
    #     '''
    #     as_,cp_=self.get_as_cp()
    #     signature = self.get_signature(tthId)
    #     self.tth_url_3 = "&as="+str(as_)
    #     self.tth_url_4 = "&cp="+str(cp_)
    #     self.tth_url_5 = "&_signature="+signature+"."
    #     self.url = self.tth_url_1+tthId+self.tth_url_2+self.tth_url_3+self.tth_url_4+self.tth_url_5
    #     self.referer = "https://www.toutiao.com/c/user/" + tthId + "/"
    #     self.header["Referer"] = self.referer
    #     self.header["User-Agent"] = self.random_select_header(self.usrAgent)
    #     # html = self.get_query_result(query_url,tthId)
    #     # print(html)

    # def get_as_cp(self):
    #     nowTime = round(time.time())
    #     e = hex(int(nowTime)).upper()[2:]
    #     i = md5(str(int(nowTime)).encode('utf-8')).hexdigest().upper()
    #     if len(e) != 8:
    #         as_ = "479BB4B7254C150"
    #         cp_ = "7E0AC8874BB0985"
    #         return as_,cp_
    #     n = i[:5]
    #     a = i[-5:]
    #     r = ""
    #     s = ""
    #     for i in range(5):
    #         s = s + n[i] + e[i]
    #     for j in range(5):
    #         r = r + e[j + 3] + a[j]
    #
    #     as_ = "A1" + s + e[-3:]
    #     cp_ = e[0:3] + r + "E1"
    #     return as_,cp_

    # def get_signature(self, user_id):
    #     """
    #     计算_signature
    #     :param user_id: user_id不需要计算，对用户可见
    #     :return: _signature
    #     """
    #     self.ctxt.__enter__()
    #     self.ctxt.eval('getSignature.txt')
    #     _signature = self.ctxt.locals.decode
    #     signature = _signature(user_id)
    #
    #     return signature

    def search_toutiao(self,keyword):
        '''
        get articles from 今日头条页面搜索
        :param keyword:
        :return:
        '''
        self.items = []
        for i in range(3):
            self.url = self.tt_search_url_1 + str(20*i)+ self.tt_search_url_2 + quote(keyword,'utf-8') + self.tt_search_url_3
            self.referer = 'https://www.toutiao.com/search/?keyword=' + quote(keyword,'utf-8')
            self.header["Referer"] = self.referer
            self.header["User-Agent"] = self.random_select_header(self.usrAgent)
            # print(self.url)
            # print(self.referer)
            self.get_random_ip()
            # print(self.proxy)
            self.getWeb()
            self.items = self.items + self.html['data']
            # print('check point: get_data')
            # time.sleep(10)

    def getWeb(self):
        proxy_support = urllib.request.ProxyHandler(self.proxy)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        self.request = urllib.request.Request(url=self.url, headers=self.header)
        self.response = urllib.request.urlopen(self.request, timeout=20)
        html = self.response.read()
        html = str(html, 'utf-8')
        self.html = json.loads(html)

    def get_hot(self,tthId):
        self.get_random_ip()
        self.url = self.tt_hot_url_1 + str(tthId)
        self.header["Accept"] = 'text/javascript,text/html,application/xml,text/xml,*/*'
        self.referer = self.tth_ID + str(tthId) + "/"
        self.header["Referer"] = self.referer
        self.header["User-Agent"] = self.random_select_header(self.usrAgent)
        # print(self.url)
        # print(self.header)
        self.get_random_ip()
        # print(self.proxy)
        self.getWeb()
        self.items = self.html['data']['hot_articles']
        # print(self.items)

    def get_tthId(self,keyword):
        self.url = self.tt_search_url_1 + str(0) + self.tt_search_url_2 + quote(keyword,'utf-8') + self.tt_search_url_3
        self.referer = 'https://www.toutiao.com/search/?keyword=' + quote(keyword, 'utf-8')
        self.header["Referer"] = self.referer
        self.header["User-Agent"] = self.random_select_header(self.usrAgent)
        self.get_random_ip()
        self.getWeb()
        self.items = self.items + self.html['data']

    def id_acquire(self):
        for i in self.items:
            if i !=[]:
                try:
                    tth_name = i["screen_name"]
                    tth_id = i["user_id"]
                    print(tth_name)
                    print(tth_id)
                    self.add_tthId(tth_name,tth_id)
                except:
                    pass

    def content_acquire(self):
        for i in self.items:
            if i != []:
                try:
                    self.title = i["title"]
                    self.time = i["datetime"][:10]
                    self.link = i["article_url"]
                    self.class_ = 'web'
                    self.channel = 'toutiao'
                    self.name_ch = i["keyword"]
                    self.name = i["media_name"]
                    # print(self.title)
                    # print(self.time)
                    # print(self.link)
                    # print(self.class_)
                    # print(self.channel)
                    # print(self.name_ch)
                    # print(self.name)
                    if self.name_ch == self.name:
                        wechat_check = re.findall(r'timestamp',self.link)
                        if wechat_check == []:
                            start = datetime.date(int(self.time[0:4]), int(self.time[5:7]), int(self.time[8:]))
                            end = datetime.date(int(str(self.t[-1])[0:4]), int(str(self.t[-1])[5:7]), int(str(self.t[-1])[8:]))
                            days = rrule.rrule(rrule.DAILY, dtstart=start, until=end).count()
                            if days <= 1:
                                state = self.write(self.name_ch, self.title, self.time, self.link, self.class_)
                                self.crawls += 1
                                if state == 0:
                                    self.fail += 1
                                    self.failname.append(self.title)
                                    self.failed_link.append(self.link)
                                elif state == 1:
                                    self.addins += 1
                                else:
                                    pass
                    else:
                        pass
                except:
                    pass

        self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
                           self.failed_link)

        self.crawls = 0
        self.addins = 0
        self.fail = 0
        self.failname = []
        self.failed_link = []

    def content_acquire_hot(self):
        for i in self.items:
            if i != []:
                try:
                    self.title = i["title"]
                    self.time = i["publish_time"][:10]
                    self.link = i["item_id"]
                    self.class_ = 'web'
                    self.channel = 'toutiao'
                    self.time = re.sub(r'/','-',str(self.time))
                    self.link = 'https://www.toutiao.com/i'+str(self.link) +'/'
                    # print(self.title)
                    # print(self.time)
                    # print(self.link)
                    # print(self.class_)
                    # print(self.channel)
                    # print(self.name_ch)
                    # print(self.name)
                    # if self.name_ch == self.name:
                        # print('check point: save_data')
                    wechat_check = re.findall(r'timestamp', self.link)
                    if wechat_check == []:
                        start = datetime.date(int(self.time[0:4]), int(self.time[5:7]), int(self.time[8:]))
                        end = datetime.date(int(str(self.t[-1])[0:4]), int(str(self.t[-1])[5:7]), int(str(self.t[-1])[8:]))
                        days = rrule.rrule(rrule.DAILY, dtstart=start, until=end).count()
                        if days <= 1:
                            state = self.write(self.name_ch, self.title, self.time, self.link, self.class_)
                            self.crawls += 1
                            if state == 0:
                                self.fail += 1
                                self.failname.append(self.title)
                                self.failed_link.append(self.link)
                            elif state == 1:
                                self.addins += 1
                            else:
                                pass
                        else:
                            pass
                except:
                    pass

        self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
                           self.failed_link)
        self.crawls = 0
        self.addins = 0
        self.fail = 0
        self.failname = []
        self.failed_link = []

    def write(self,name_ch,title,time,link,class_):
        exist = self.exist_detecter(title)
        if exist == 1:
            self.availables_web = self.cruiser_to_list(self.db.NEWS_toutiao.find({}), "title")
            self.simId = self.duplicate_id_generator(title, self.availables_web)
            del self.availables_web
            if self.simId == None:
                try:
                    self.db.NEWS_toutiao.insert_one({
                        "source": name_ch, "coll_date": self.t[-1],
                        "date": time, "title": title,
                        "class": class_, "link": link,
                        "screen": True, "collect": False,"channel":self.channel})
                    print('"%s" has successfully been saved' % str(title))
                    return (1)
                except:
                    return (0)

            else:
                print('"%s" has a similar article' % str(title))
                try:
                    self.db.NEWS_toutiao.insert_one({
                        "source": name_ch, "coll_date": self.t[-1],
                        "date": time, "title": title,
                        "class": class_, "link": link,
                        "screen": True, "collect": False, "sim_news": self.simId,"channel":self.channel})
                    return (2)
                except:
                    return (0)
        else:
            print('"%s" exists' % str(title))
            return (2)

    def work_flow(self):
        self.get_proxy()
        self.get_source()
        for i in self.wechat_list:
            print("start collecting %s" %str(i))
            self.search_toutiao(str(i))
            self.content_acquire()
        self.get_source_tthId()
        for i in self.tth_Id_list:
            print("start collecting hot_news of tth %s" %str(i[0]))
            self.get_hot(str(i[1]))
            self.name_ch = str(i[0])
            self.name = str(i[0])
            self.content_acquire_hot()

    def get_source(self):
        source = self.db.WECHAT_LIST.find({})
        dict = [doc for doc in source]
        self.wechat_list = [i["source_name"] for i in dict]
        return self.wechat_list

    def get_source_tthId(self):
        source = self.db.WECHAT_LIST.find({"tth_id":{"$exists":True}})
        dict = [doc for doc in source]
        tthId_list = [i["tth_id"] for i in dict]
        tth = [i["source_name"] for i in dict]
        self.tth_Id_list = list(zip(tth,tthId_list))

    def id_flow(self):
        self.get_proxy()
        self.get_source()
        for i in self.wechat_list:
            self.get_tthId(i)
            self.id_acquire()

    def add_tthId(self,tth,tthId):
        source = self.db.WECHAT_LIST.find({"tth_id":{"$exists":False}})
        for i in source:
            if i["source_name"] == str(tth):
                self.db.WECHAT_LIST.update({"source_name":str(tth)},{'$set': {"tth_id": str(tthId)}},True,True)
                print('tth:{} with id:{} is added'.format(str(tth),str(tthId)))
            else:
                pass

if __name__ == "__main__":
    T = toutiao()
    T.work_flow()