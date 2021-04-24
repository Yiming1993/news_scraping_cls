# 一个新闻爬取和智能推送的系统（A news scraping and recommending system）

##近期更新
2018-04-02：更新techcrunch.py和theatlantic.py，修复无法爬取数据的错误；添加spider_update.py，准备代码优化工作
2018-04-08：优化所有爬虫代码，提升运行速度，降低内存占用；优化了容错和每日日志功能
2018-04-11: 增加label_reading.py，可批量统计tag，根据tag搜索news，以及批量或对单个news的tag进行增加，删除和替换（见label_reading.py内说明）
预定于2018-05-01前：优化CNN筛选方法，降低FP数量

## 组件

1. web spider

bbc.py

cbs.py

futurism.py

kr.py

kr-path.py

leifeng.py

mirror.py

mit.py

netease.py

netease-path.py

sina.py

spectrum.py

techcrunch.py

techrepublic.py

theatlantic.py

venturebeat.py

wired.py

yiou.py

zdnet.py

以上文件分别对应一个网站爬虫

2. wechat spider

wechat.py

对应任意微信公众号文章爬虫

3. CNN

（1）CNN组件

text_cnn.py 

train.py

eval.py

data_helper.py

（2）数据获取组件

getdata.py

 seg_data.py

（3）CNN主函数

screen.py

（4）每日报告

data_reading.py

4. 基类，main函数

spider.py 为爬虫基类，包括网络请求函数，新闻去重和存储函数

web-main.py 用来调用web spider和CNN

wechat-main.py 用来调用wechat spider



## 工作流程

1. 运行web-main.py
2. 对每一个爬虫：

爬取新闻，生成包括新闻标题，URL和日期的新闻列表

spider.py中的write()遍历新闻列表，并去重，存入数据库

3. 爬虫数据全部存储完毕后，输出fail list
4. web-main.py调用screen.py，启动CNN
5. CNN收集历史新闻数据训练（pos：当天的前一天向前300天；neg：当天的前一天向前7天）
6. 获得当天的模型，对当天爬取的web news筛选
7. 获得筛选结果后更新数据库，增加“alg1_collect”键，True为选择，False为不选择
8. 由网页端直接调用wechat.py，运行微信爬虫
9. 微信爬虫去重后直接存入数据库
10. 当天新闻收集后第二天，运行data_reading.py，获得CNN筛选的报告



## 注意事项

1. CNN筛选时会生成config.txt文件，用来引导getdata.py收集数据，该文件会在下一次运行CNN时被更新
2. 每天第一次运行CNN时会将前一天的模型删除并保存今天的模型，路径为"./runs"，该模型会保存一天，用于对分批存入的news筛选。当天过后，第二天再次运行CNN时，模型会被更换
