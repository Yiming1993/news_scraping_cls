#coding='utf-8'

from pymongo import MongoClient
import datetime
from dateutil import parser
import jieba
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from gridfs import *
import matplotlib.pyplot as plt
import re

def str2time(testdate):
    datetime_struct = parser.parse(testdate)
    return datetime_struct

def define_dates(time):
    start_date_time = time + datetime.timedelta(days=-8)
    end_date_time = time + datetime.timedelta(days=-1)
    start_date = str(start_date_time)[:10]
    end_date = str(end_date_time)[:10]
    return start_date, end_date

class Cloud(object):
    def __init__(self):
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name]
        self.today = str(datetime.datetime.now())[:10]
        self.start_date, self.end_date = define_dates(str2time(self.today))
        self.client = client

    def cal_word(self, topK = 100):
        jieba.load_userdict('./References/dict.txt')
        stopwords = [line.strip() for line in open('./References/stop.txt', 'r',encoding='utf-8').readlines()]
        text = ''
        word_dict = {}
        news = self.db.NEWS.find({'$and': [{'collect': True}, {"coll_date": {'$gte': self.start_date}}, {"coll_date": {'$lte': self.end_date}}]})
        for doc in news:
            title = doc["title"]
            text += title
        cut_words = jieba.lcut(text)
        cut_words = [i for i in cut_words if i not in stopwords]
        for i in cut_words:
            if i not in word_dict:
                word_dict[i] = 1
            else:
                word_dict[i] = word_dict[i] + 1
        sort_dict = sorted(word_dict.items(), key = lambda x:x[1], reverse=True)
        return [i[0] for i in sort_dict][:topK]

    def word_cloud(self, topK=100):
        jieba.load_userdict('./References/dict.txt')
        stopwords = [re.sub(r'\n','',str(line)) for line in open('./References/stop.txt', 'r',
                                                   encoding='utf-8').readlines()]
        text = ''
        news = self.db.NEWS.find({'$and': [{'collect': True}, {"coll_date": {'$gte': self.start_date}},
                                           {"coll_date": {'$lte': self.end_date}}]})
        for doc in news:
            title = doc["title"]
            text += title
        cut_words = jieba.lcut(text)
        cut_words = ' '.join([i for i in cut_words if i not in stopwords])
        font_path = './HOTSPOT/simhei.ttf'
        bg_image = plt.imread('color.jpg')
        img_colors = ImageColorGenerator(bg_image)
        wc = WordCloud(font_path=font_path,
                       background_color='white',
                       max_words=topK,
                       min_font_size=60,
                       max_font_size=300,
                       width=1500,
                       height=1500,
                       relative_scaling=0.5,
                       prefer_horizontal=1).generate(cut_words)
        wc.recolor(color_func=img_colors)
        wc.to_file('hot_words.png')
        self.save_pic('hot_words.png')
        print('cloud pic is saved successfully')

    def save_pic(self, file_path):
        self.db.fs.chunks.remove()
        self.db.fs.files.remove()
        datatmp = open(file_path, 'rb')
        imgput = GridFS(self.db)
        imgput.put(datatmp, content_type='png', filename='hot_words', gen_date = self.today)
        datatmp.close()

if __name__ == '__main__':
    W = Cloud()
    W.word_cloud(200)
