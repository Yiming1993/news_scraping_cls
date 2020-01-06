#coding = 'utf-8'
from pymongo import MongoClient
from bs4 import BeautifulSoup
import random
import re
import json
import urllib.request
import ssl
import time
from bson import ObjectId
import datetime

ssl._create_default_https_context = ssl._create_unverified_context

class Content_spider(object):
    def __init__(self):
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name]
        self.usrAgent = [
            "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
            "Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15",
        ]
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Pragma': 'no-cache',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Accept-Language': 'zh-cn',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.type_content = ["tech","industry","cross"]
        self.type_genre = ["genre"]
        self.ch_list = ['36氪', '新浪科技', '网易智能', '亿欧', '雷锋网', '36Kr', '网易科技']
        self.proxy_path = '../References/proxy.txt'
        self.today = str(datetime.datetime.now())[:10]

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
        ip_ = open(self.proxy_path, 'r').readlines()
        ip_list = [re.sub(r'\n','',str(i)) for i in ip_]
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
        bsObj = BeautifulSoup(response, 'lxml')
        return bsObj

    def get_wechat(self,url):
        self.header["User-Agent"] = self.random_select_header(self.usrAgent)
        self.header["Host"] = 'mp.weixin.qq.com'
        proxy_support = urllib.request.ProxyHandler(self.proxy)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        request = urllib.request.Request(url=url, headers=self.header)
        response = urllib.request.urlopen(request, timeout=20)
        html = str(response.read(), 'utf-8')
        text = self.process_wechat(html)
        return text

    def process_wechat(self,html):
        soup = BeautifulSoup(html,'lxml')
        wechat_text = soup.findAll('span')
        text = ''
        for i in wechat_text:
            text += self.format_same(i.get_text())
        return text

    def format_same(self,text):
        text1 = re.sub(r'\n','',str(text))
        text2 = re.sub(r"'",'',str(text1))
        text3 = re.sub(r'\s+','',str(text2))
        return text3

    def get_web(self,url,source_):
        def process_36kr(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _script = soup.findAll('script')[7]
            _text = re.sub(r'<[^>]+>', '', str(_script))
            _text = re.sub(r'var\sprops=', '', str(_text))
            _text = _text.split(',')
            for i in _text:
                if 'content' in i:
                    text = re.sub(r'"', '', str(i))
                    text = re.sub(r'content','',str(text))
                    text = re.sub(r':','',str(text))
                    text = re.sub(r'&quot;','',str(text))
                    return text

        def process_sina(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\s', '', str(text))
                content += text
            return content

        def process_iyou(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[id="post_description"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\s', '', str(text))
                content += text
            return content

        def process_leifeng(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="lph-article-comView"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\s', '', str(text))
                content += text
            return content

        def process_netease(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\s', '', str(text))
                content += text
            return content

        def process_ZDNet(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="storyBody"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_VentureBeat(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="article-content"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_Atlantic(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('section[class="l-article__section s-cms-content"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_MIT(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="article-body__content"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_wired(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('article[class="article-body-component article-body-component--science"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_techRepublic(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_techCrunch(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="article-content"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_IEEESpectrum(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="articleBody entry-content"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_BBC(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="story-body__inner"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_Mirror(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[class="article-body"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_cbs(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('div[id="article-entry"] p')
            content = ''
            for i in _text:
                text = re.sub(r'<[^>]+>', '', str(i))
                text = re.sub(r'\n', '', str(text))
                text = re.sub(r'\s+', ' ', str(text))
                content += text
            return content

        def process_futurism(html):
            # print(html)
            soup = BeautifulSoup(html, 'lxml')
            _text = soup.select('script')[-7]
            story = re.sub(r'<[^>]+>','',str(_text))
            content = story.split('"content":')[-1]
            text = content.split('READ')[0]
            text = text.encode('utf-8').decode('unicode-escape')
            text = re.sub(r'<[^>]+>','',str(text))
            text = re.sub(r'&#[0-9]{4};','',str(text))
            text = re.sub(r'\n','',str(text))
            return text

        self.header = {}
        self.header["User-Agent"] = self.random_select_header(self.usrAgent)
        source = self.kill_ufeff(source_)
        if source == "36氪" or source == "36Kr":
            self.header["Host"] = "36kr.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=20)
                html = str(response.read(), 'utf-8')
                text = process_36kr(html)
                return text
            except:
                text = ''
                return text

        if source == "新浪科技":
            self.header["Host"] = "tech.sina.com.cn"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
            except:
                time.sleep(10)
                try:
                    proxy_support = urllib.request.ProxyHandler(self.proxy)
                    opener = urllib.request.build_opener(proxy_support)
                    urllib.request.install_opener(opener)
                    request = urllib.request.Request(url=url, headers=self.header)
                    response = urllib.request.urlopen(request, timeout=60)
                    html = str(response.read(), 'utf-8')
                    text = process_sina(html)
                    return text
                except:
                    text = ''
                    return text

        if source == "亿欧":
            self.header["Host"] = "www.iyiou.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_iyou(html)
                return text
            except:
                text = ''
                return text


        if source == "雷锋网":
            self.header["Host"] = "www.leiphone.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
            except:
                text = ''
                return text
            html = str(response.read(), 'utf-8')
            text = process_leifeng(html)
            return text

        if source == "网易智能":
            self.header["Host"] = "tech.163.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_netease(html)
                return text
            except:
                time.sleep(10)
                try:
                    proxy_support = urllib.request.ProxyHandler(self.proxy)
                    opener = urllib.request.build_opener(proxy_support)
                    urllib.request.install_opener(opener)
                    request = urllib.request.Request(url=url, headers=self.header)
                    response = urllib.request.urlopen(request, timeout=60)
                    html = str(response.read(), 'utf-8')
                    text = process_netease(html)
                    return text
                except:
                    text = ''
                    return text

        if source == "ZDNet":
            self.header["Host"] = "www.zdnet.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_ZDNet(html)
                return text
            except:
                text = ''
                return text

        if source == "VentureBeat":
            self.header["Host"] = "venturebeat.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_VentureBeat(html)
                return text
            except:
                text = ''
                return text

        if source == "The Atlantic":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_Atlantic(html)
                return text
            except:
                text = ''
                return text


        if source == "MIT Technology Review":
            self.header["Host"] = "www.technologyreview.com"
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_MIT(html)
                return text
            except:
                text = ''
                return text

        if source == "WIRED":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_wired(html)
                return text
            except:
                text = ''
                return text

        if source == "TechRepublic":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_techRepublic(html)
                return text
            except:
                text = ''
                return text

        if source == "TechCrunch":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_techCrunch(html)
                return text
            except:
                text = ''
                return text

        if source == "IEEE Spectrum":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_IEEESpectrum(html)
                return text
            except:
                text = ''
                return text

        if source == "BBC":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_BBC(html)
                return text
            except:
                text = ''
                return text

        if source == "Mirror":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_Mirror(html)
                return text
            except:
                text = ''
                return text

        if source == "CBS":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_cbs(html)
                return text
            except:
                text = ''
                return text

        if source == "Futurism":
            try:
                proxy_support = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.header)
                response = urllib.request.urlopen(request, timeout=60)
                html = str(response.read(), 'utf-8')
                text = process_futurism(html)
                return text
            except:
                text = ''
                return text

        return ''

    def kill_ufeff(self, url):
        return re.sub(r'\ufeff','', str(url))

    def save_proxy(self):
        bsObj = self.get_proxy()
        ip_list = self.get_ip_list(bsObj)
        for i in ip_list:
            f = open('../References/proxy.txt','a')
            f.write(str(i) + '\n')
            f.close()
        print('proxy is saved')

    def work_flow(self, spider_order, source, url):
        self.get_random_ip()
        url = self.kill_ufeff(url)
        if spider_order == 'wechat':
            text = self.get_wechat(url)
        else:
            text = self.get_web(url, source)
        return text

    def save_article(self, startdate, enddate):
        news = self.db.NEWS.find({"$and":[{"coll_date": {'$gte': startdate}}, {"coll_date": {'$lte': enddate}},{"$or":[{"content":{"$exists":False}}]}]})
        for i in news:
            newsId = i["_id"]
            class_ = i["class"]
            source = i["source"]
            link = i["link"]
            title = i["title"]
            content = self.work_flow(class_, source, link)
            if content != '' or content != 'None' or content != None:
                self.db.NEWS.update({"_id":ObjectId(newsId)},{"$set":{"content":str(content)}}, True, True)
                print('Article: {} is saved'.format(str(title)))
            else:
                print('Article: {} failed'.format(str(title)))

if __name__ == "__main__":
    G = Content_spider()
    # G.save_proxy()
    G.save_article('2018-01-01','2018-11-19')