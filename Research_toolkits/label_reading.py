from pymongo import MongoClient
from bson import ObjectId
import re
'''
label_reading.py是用于对数据库内的label进行搜索，统计和修改的工具
"label_calculation(label_name)":输入label的名称，可以返回该标签内的新闻数量
"label_classification(class_list)":输入一个class的list，返回该class内所有标签的下新闻的数量
"get_labels()":获得所有label，返回一个list
"label_search(label_name)":根据label搜索其下的新闻id和title
"label_change_all(label_name_before,*label_name_after,mode="modify")":变更所有新闻的标签，有
"modify"，"append"，"remove"三种模式，默认为modify
modify模式下：需要输入需要变更的标签名，变更后的标签名
append模式下：只需要输入要添加的标签名，并选择mode="append"
remove模式下：只需要输入要删除的标签名，并选择mode="remove"
"label_change_single_news(newsId,label_name_before,*label_name_after,mode="modify")":
变更选定新闻的标签，模式和label_change_all类似，但需要在输入label_name前先输入newsId
'''

class1 = ['区块链','大数据','人工智能','政策','机器人','智能语音','云计算','硬件',
                       '教育','软件','自动驾驶','智能家居','智慧医疗','智慧城市',
                       'AR','VR','Chatbots','投资','融资','产品','机器学习',
                       '智能制造','物联网','社科研究','业界','金融','社会事件','blockchain',
                       '创业','神经网络','深度学习','计算机视觉','人才','交通','量子计算',
                       '无人机','零售','保险','房地产','自然语言处理','国际局势','社交网络',
                       '艺术界','智慧安防','人脸识别','汽车行业','安全','伦理道德']

class2 = ['会议','公开课','专家评论','报告','数据集','科学研究','活动预告',
        '论文','应用落地','合作','技术详解','发展趋势',]

class_tech_1 = ['区块链', '大数据', '人工智能', '机器人', '云计算', 'AR', 'VR', '物联网', '计算机视觉', '量子计算', '自然语言处理', '语音处理', '图像处理']
class_tech_2 = ['机器学习', '神经网络', '深度学习', '无人机', 'AI芯片', '强化学习']

class_industry_1 = ['教育', '金融', '交通', '零售', '保险', '房地产', '医疗', '城市', '安防', '制造', '物流', '社科']
class_industry_2 = ['自动驾驶', '社交网络', '新能源汽车', '共享出行', '舆情分析', '金融科技']

class_genre_1 = ['政策', '报告', '评论', '分析', '新闻事件']
class_genre_2 = ['专家评论', '投资', '融资', '产品', '社会事件', '创业', '合作', '国际局势', '伦理道德', '媒体评论', '技术报告', '行业报告', '政策文件', '政策解读', '前沿技术', '新算法', '代码详解', '产品分析', '商业分析', '市场趋势', '人才培训', '战略']

class_cross = ['智慧医疗', '智慧城市', '智能制造', '智慧安防', '智慧出行', '智慧物流', '科技金融']


class label_reading(object):
    def __init__(self):
        host = ''
        port = ''
        user_name = ''
        user_pwd = ''
        db_name = ''
        uri = "mongodb://" + user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
        client = MongoClient(uri)
        self.db = client[db_name]

    def label_calculation(self, label_name):
        news = self.db.NEWS.find({"collect":True})
        label_num = 0
        for doc in news:
            try:
                label_list = doc["tag"]
                label = label_list.count(label_name)
                if label > 0:
                    label_num += 1
            except:
                continue
        # print((label_name,label_num))
        return (label_name,label_num)

    def label_classficaition(self,class_list):
        label_list_num = [self.label_calculation(i) for i in class_list]
        label_list_num.sort(key=lambda x:x[1], reverse=True)
        print(label_list_num)
        return label_list_num

    def get_labels(self):
        tags = self.db.TAGS.find({})
        labels = [doc["name"] for doc in tags]
        return labels

    def label_search(self,lable_name):
        news = self.db.NEWS.find({"collect": True})
        for doc in news:
            try:
                news_id = doc["_id"]
                news_title = doc["title"]
                label_list = doc["tag"]
                title_list = [(news_id,news_title) if str(lable_name) in label_list else None]
                if None not in title_list:
                    print(title_list)
            except:
                continue

    def label_change_all(self,label_name_before,*label_name_after,mode="modify"):
        news = self.db.NEWS.find({"collect": True})
        for doc in news:
            try:
                newsId = doc["_id"]
                label_list = doc["tag"]

                if mode == "modify":
                    new_label_list = [str(label_name_after[0]) if x == str(label_name_before) else x for x in
                                      label_list]

                elif mode == 'remove':
                    label_list.remove(str(label_name_before))
                    new_label_list = label_list

                elif mode == 'append':
                    if str(label_name_before) not in label_list:
                        label_list.append(str(label_name_before))
                    else:
                        print('new label %s already exists' % str(label_name_before))
                    new_label_list = label_list
                else:
                    raise ('Incorrect input mode')

                print('news: %s' % str(newsId))
                print('previous label: %s' % str(label_list))
                self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"tag": new_label_list}}, True, True)
                print('new label: %s' % str(new_label_list))
            except:
                continue

    def label_change_single_news(self,newsId,label_name_before,*label_name_after,mode="modify"):
        target_news = self.db.NEWS.find({"_id": ObjectId(str(newsId))})
        for doc in target_news:
            print('target news: %s' % str(newsId))
            label_list = doc["tag"]
            print('previous label: %s' % str(label_list))
            if mode == "modify":
                new_label_list = [str(label_name_after[0]) if x == str(label_name_before) else x for x in label_list]
            elif mode == 'remove':
                label_list.remove(str(label_name_before))
                new_label_list = label_list
            elif mode == 'append':
                if str(label_name_before) not in label_list:
                    label_list.append(str(label_name_before))
                else:
                    print('new label %s already exists' % str(label_name_before))
                new_label_list = label_list
            else:
                raise ('Incorrect input mode')
            self.db.NEWS.update({"_id": ObjectId(newsId)}, {'$set': {"tag": new_label_list}}, True, True)
            print('new label: %s' % str(new_label_list))
            print('news %s tag is modified' % str(newsId))

    def label_search_single_news(self,newstitle):
        target_news = self.db.NEWS.find({"$and":[{'title':newstitle},{'collect':True}]})
        return [i["tag"] for i in target_news][0]

    def restore_tags(self,tag_name,tag_num):
        if tag_name in class_tech_1:
            bg_clr = '#FFD700'
            fnt_clr = 'rgb(255,215,0)'
            level = 1
            class_ = 'tech'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_tech_2:
            bg_clr = '#FF8000'
            fnt_clr = 'rgb(255,128,0)'
            level = 2
            class_ = 'tech'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_industry_1:
            bg_clr = '#00C957'
            fnt_clr = 'rgb(0,201,87)'
            level = 1
            class_ = 'industry'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_industry_2:
            bg_clr = '#228B22'
            fnt_clr = 'rgb(34,139,34)'
            level = 2
            class_ = 'industry'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_genre_1:
            bg_clr = '#87CEEB'
            fnt_clr = 'rgb(135,206,235)'
            level = 1
            class_ = 'genre'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_genre_2:
            bg_clr = '#0000FF'
            fnt_clr = 'rgb(0,0,255)'
            level = 2
            class_ = 'genre'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)
        if tag_name in class_cross:
            bg_clr = '#808A87'
            fnt_clr = 'rgb(128,138,135)'
            level = 1
            class_ = 'cross'
            self.save_tag(tag_name, tag_num, bg_clr, fnt_clr, level, class_)

    def save_tag(self,tag_name,tag_num,bg_clr,fnt_clr,level,class_):
        self.db.TAGS.insert({"name":tag_name,"number":tag_num,"collect":False,
                             "level":level,"class":class_,"show":0,"bg_clr":bg_clr,
                             "fnt_clr":fnt_clr})
        print('tag %s is restored' %str(tag_name))

    def sort_tags(self):
        f = open('/Users/Yiming/Desktop/new-spider/yzc/new-spider-alpha/References/tags_backup.txt')
        tag_lists = [re.sub(r'\n','',str(i)) for i in f]
        technology = []
        content = []
        genre = []
        cross = []
        for i in range(len(tag_lists)):
            if i in range(1,20):
                # print('technology')
                # print(tag_lists[i])
                technology.append(tag_lists[i])
            elif i in range(21,39):
                # print('content')
                # print(tag_lists[i])
                content.append(tag_lists[i])
            elif i in range(40,67):
                # print('genre')
                # print(tag_lists[i])
                genre.append(tag_lists[i])
            elif i == 0 or i== 20 or i == 39 or i== 67:
                pass
            else:
                # print('cross')
                # print(tag_lists[i])
                cross.append(tag_lists[i])

        return technology+content+genre+cross


if __name__ == "__main__":
    D = label_reading()
    all_tags = D.sort_tags()
    iterT = 1
    for i in range(len(all_tags)):
        D.restore_tags(all_tags[i],iterT)
        iterT +=1