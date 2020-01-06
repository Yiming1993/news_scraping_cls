from pymongo import MongoClient
import datetime
from bson import ObjectId
import jieba.analyse
import os
import jieba
import re
import json

class add_tag(object):
    def __init__(self):
        '''
        初始化相关信息，如数据库地址，定义数字列表，中文新闻列表，并确定今日日期
        '''
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name] #数据库接口
        self.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                        '百', '千', '万', '亿', '兆'] #数字信息用于进行关键词过滤，可考虑删除
        self.ch_list = ['36氪', '新浪科技', '网易智能', '亿欧', '雷锋网', '36Kr', '网易科技'] #中文新闻列表
        self.today = str(datetime.datetime.now())[:10] #今日日期，取完整日期的前10位，即：YYYY-MM-DD
        print(self.today)

    def get_news(self):
        '''
        :return: 直接过去今日新闻的标题和id
        '''
        newslist_today = []
        newsID_today = []
        news_today = self.db.NEWS.find({"$and":[{"collect":True},{"coll_date":self.today},{"tag":{"$exists":False}}]})
        for doc in news_today:
            newslist_today.append(doc["title"])
            newsID_today.append(doc["_id"])

        return newslist_today,newsID_today

    def TF(self, seged_sentence, topK=100, withWeight=False):
        '''
        :param seged_sentence: 已分词的新闻，为一个list
        :param topK: TF的前几位
        :param withWeight: 是否提供词频，默认为不提供
        :return: 返回词频在前topK的词语
        '''
        word = []
        counterColl = {}
        for w in seged_sentence:
            if w != ' ':
                if w != '':
                    if len(w) > 1:
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

    def TF_IDF(self, data, topK=100,withWeight=False):
        '''
        :param data: 新闻标题的分词结果，数据类型为list
        :param topK: 同TF，为TF-IDF值从高到低的前topK位
        :param withWeight: 是否返回TF-IDF值，默认为否
        :return: TF-IDF值最高的前topK位词语
        '''
        sentence = ''
        for i in data:
            sentence += i
            sentence += ' ' #将分词变为jieba可接受的形式
        return jieba.analyse.extract_tags(sentence,topK=topK, withWeight=withWeight)

    def rule_single(self,label_name,type="TF",topK=100):
        '''
        构建每一个标签的关键词词表
        :param label_name: 需要构建词表的标签名
        :param type: 构建关键词的算法，默认为词频算法
        :param topK: 构建的关键词数量，默认为100个词
        :return: 该标签下TF或TF-IDF值最高的前100个词语组成的关键词表
        '''
        tag_keywords = ''
        newspool = self.db.NEWS.find({"$and":[{"collect": True},{"tag":{"$exists":True}}]})
        for doc in newspool:
            newstitle = doc["title"]
            tags = doc["tag"]
            if label_name in tags:
                tag_keywords += newstitle

        if type=="TF":
            keywords_list = self.TF(self.seg_sentence(tag_keywords).split(" "),topK=topK)
        else:
            keywords_list = self.TF_IDF(self.seg_sentence(tag_keywords).split(" "),topK=topK)
        return keywords_list

    def all_rules(self,type="TF",mode="both",topK=100):
        '''
        构建所有标签的关键词词表的程序
        :param type: 算法类型，默认为TF
        :param mode: 构建模式，是分开构建还是统一构建，默认为统一
        :param topK: 关键词词表大小，默认为100
        :return:
        '''
        if mode == "tech": #tech类别的标签，包括了tech，industry和cross三种
            tagpool = self.db.TAGS.find({"$or":[{"class":"tech"},{"class":"industry"},{"class":"cross"}]})
            tags = [i["name"] for i in tagpool]
            rules = [(i,self.rule_single(i, type=type, topK=topK)) for i in tags]
            return rules
        elif mode == "genre": #genre类别的标签，只有genre一种
            tagpool = self.db.TAGS.find({"class": "genre"})
            tags = [i["name"] for i in tagpool]
            rules = [(i,self.rule_single(i, type=type, topK=topK)) for i in tags]
            return rules
        else: #对过去旧标签的规则进行构建，已不再使用
            tagpool = self.db.TAGS.find({"class": {"$ne": "old"}})
            tags = [i["name"] for i in tagpool]
            rules = [(i,self.rule_single(i, type=type, topK=topK)) for i in tags]
            return rules

    def english_to_chinese(self,sentence):
        '''
        英文关键词转换为中文关键词
        :param sentence:
        :return: 英文关键词对应的中文关键词
        '''
        word = re.sub(r'AI','人工智能',str(sentence))
        word = re.sub(r'IoT','物联网',str(word))
        word = re.sub(r'Blockchain','区块链',str(word))
        return word

    def seg_sentence(self,sentence):
        '''
        分词程序
        :param sentence: 新闻标题
        :return: 分词并去除了停用词的新闻标题
        '''
        jieba.load_userdict('/Users/Yiming/Desktop/new-spider-alpha/References/dict.txt')
        stopwords = [line.strip() for line in open('/Users/Yiming/Desktop/new-spider-alpha/References/stop.txt', 'r', encoding='utf-8').readlines()]
        sentence_seged = jieba.cut(sentence.strip())
        outstr = ''
        for word in sentence_seged:
            if word not in stopwords:
                if word != '\t':
                    if word != '':
                        if word != ' ':
                            if word != '\xa0':
                                if len(word) > 1:
                                    word = self.english_to_chinese(word)
                                    outstr += word
                                    outstr += " "
        return outstr

    def matching_news(self,newstitle,rules):
        '''
        判断标签和新闻相似度的程序
        :param newstitle: 新闻标题
        :param rules: 所有标签及附带的关键词表
        :return:
        '''
        prob_pool = {}
        keywords_news = [i for i in self.seg_sentence(newstitle).split(" ") if i!='']
        for i in rules:
            if i[0] in keywords_news:
                prob_pool[i[0]] = 100 #如果标题内有标签，则该标签权重提高100倍
            else:
                prob_pool[i[0]] = self.jaccard_similarity(keywords_news, i[1])
                #否则，使用jaccard similarity计算新闻标题和该标签的相似度
        final_tags = sorted(prob_pool.items(), key=lambda x: x[1], reverse=True)
        final_tag_list = [i[0] for i in final_tags] #降序排列和新闻相似度高的标签
        return final_tag_list

    def jaccard_similarity(self,x,y):
        intersection = len(set.intersection(*[set(x), set(y)])) #jaccard similarity，两个list的交集除以并集
        union = len(set.union(*[set(x), set(y)]))
        return intersection / float(union)

    def artificial_similarity(self,x,y):
        intersection = len(set.intersection(*[set(x), set(y)])) #人为设定的相似度算法，使用交集除以被计算的list长度，现已不再使用
        if len(y) != 0:
            return intersection/float(len(y))
        else:
            return 0

    def intersection_list(self,x,y):
        intersection_list = list(set(x).intersection(set(y))) #构建两个list的并集，已不再使用
        return intersection_list

    def final_tags_generator(self,news,rules):
        final_tags = self.matching_news(news, rules) #收集排列好的标签
        return final_tags

    def save_model(self,model1,model2):
        '''
        保存标签算法计算后的模型
        :param model1: 和tech，industry，cross标签有关的模型
        :param model2: 和genre有关的模型
        :return: 不返回结果，但在Auto_tag文件夹内生成tag_rules1.json和tag_rules2.json两个模型文件，
        分别对应 model1 和 model2
        '''
        data = []
        if os.path.isfile('./Auto_tag/tag_rules1.json') == True:
            os.remove('./Auto_tag/tag_rules1.json')
        if os.path.isfile('./Auto_tag/tag_rules2.json') == True:
            os.remove('./Auto_tag/tag_rules2.json')
        f = open('./Auto_tag/tag_rules1.json','w',encoding='utf-8')
        for i in model1:
            pre_data = {str(i[0]):str(i[1])} #打包模型，一个标签对应一个关键词列表
            data.append(pre_data)
        json.dump(data, f, ensure_ascii=False) #保存模型
        f.close()
        data = []
        f = open('./Auto_tag/tag_rules2.json', 'w', encoding='utf-8')
        for i in model2:
            pre_data = {str(i[0]): str(i[1])}
            data.append(pre_data)
        json.dump(data, f, ensure_ascii=False)
        f.close()
        print('Rules for tags are saved')

    def reload_json(self,element):
        '''
        加载模型
        :param element: 每一个json文件中的元素
        :return: tag，及对应的关键词列表"rule"
        '''
        for tag,rule in element.items():
            rule = re.sub(r'\[','',str(rule))
            rule = re.sub(r']','',str(rule))
            rule = re.sub(r"'",'',str(rule))
            rule = re.sub(r'\s','',str(rule))
            return tag,rule.split(",")

    def load_model(self):
        '''
        加载模型
        :return: 完整的原始模型数据，分别是内容标签和体裁标签的模型
        '''
        f = open('./Auto_tag/tag_rules1.json','r',encoding='utf-8')
        rule_lines1 = json.load(f)
        rule1 = [self.reload_json(i) for i in rule_lines1]
        f = open('./Auto_tag/tag_rules2.json','r',encoding='utf-8')
        rule_lines2 = json.load(f)
        rule2 = [self.reload_json(i) for i in rule_lines2]
        return rule1, rule2

    def cover_alert(self,newstitle,taglist1,taglist2):
        '''
        判断是否覆盖了标签，已弃用
        :param newstitle: 新闻标题
        :param taglist1: 实际的内容标签列表
        :param taglist2: 实际的体裁标签列表
        :return: 是否覆盖目标的flag
        '''
        tag_cover = self.intersection_list(taglist1,taglist2)
        if taglist1 == tag_cover:
            f = open('./Auto_tag/tags_pred.txt', 'a')
            f.write(str(newstitle)+'\n'+'tag_num to cover all: ' + str(len(taglist2)) + '\n')
            f.close()
            return 1
        else:
            return 0

    def remove_covered(self,order,wholelist):
        '''
        在不改变list顺序的情况下去除元素，已弃用
        :param order:
        :param wholelist:
        :return:
        '''
        wholelist.pop(order)

    def get_new_news(self):
        '''
        获得每日新闻
        :return: 今日新闻标题列表和id列表
        '''
        newslist_today = []
        newsID_today = []
        news_today = self.db.NEWS.find({"$and": [{"collect": True}, {"tag": {"$exists": True}}]})
        for doc in news_today:
            newslist_today.append(doc["title"])
            newsID_today.append(doc["_id"])
        return newslist_today, newsID_today

    def add_tag(self,newsId,final_tags1,final_tags2):
        # print(newsId)
        # print(final_tags1)
        # print(final_tags2)
        '''
        在数据库中增加推荐标签列表
        :param newsId: 新闻id
        :param final_tags1: 内容标签排序
        :param final_tags2: 体裁标签排序
        :return:
        '''
        self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"alg1_tag_content": final_tags1}}, True, True)
        self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"alg1_tag_genre": final_tags2}}, True, True)

    def run(self):
        '''
        训练函数
        :return: 获得rule1和rule2，并保存模型
        '''
        rules1 = self.all_rules(type="TF-IDF", mode="tech", topK=70)
        rules2 = self.all_rules(type="TF-IDF", mode="genre", topK=70)
        self.save_model(rules1,rules2)

    def run_add_tag(self):
        '''
        加载今日标签模型，并保存信息
        :return:
        '''
        newslist, newsId = self.get_news()
        # print(newslist)
        news_with_tags = list(zip(newslist, newsId))
        rules1, rules2 = self.load_model()
        # print(rules1)
        # print(rules2)
        for i in news_with_tags:
            final_tags_1 = self.final_tags_generator(i[0], rules1)
            final_tags_2 = self.final_tags_generator(i[0], rules2)
            self.add_tag(i[1], final_tags_1, final_tags_2)
        print('news today is all tagged')

if __name__ == "__main__":
    A = add_tag()
    A.run()
    A.run_add_tag()