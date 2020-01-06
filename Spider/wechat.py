# coding=utf-8
import re
from spider import Spider
import urllib.request
from bs4 import BeautifulSoup
import datetime

class WechatSpider(Spider):
	def __init__(self):
		super(WechatSpider, self).__init__('wechat', "wechat", 'wechat', 'web')
		self.today = str(datetime.datetime.now())[:10]
		
	def content_acquire(self):
		self.Wechat = self.db.NEWNEWS.find({"coll_date":self.t[-1]})
		print(self.t[0])
		for doc in self.Wechat:
			self.address = doc["link"]
			self.address = str(self.address)
			self.link = re.sub(r'\ufeff', '', self.address)
			if self.link != '':
					try:
						self.request = urllib.request.Request(url=self.link, headers=self.header)
						self.response = urllib.request.urlopen(self.request, timeout=20)
						self.html = str(self.response.read(), 'utf-8')
						self.soup = BeautifulSoup(self.html, 'lxml')
						self.title = self.soup.select("h2[class='rich_media_title']")
						self.title = re.sub(r'<[^>]+>', '', str(self.title[0]))
						self.title = re.sub(r'\s+', '', str(self.title))
						self.title = re.sub(r'if[^>]+write','',str(self.title))
						self.title = re.sub(r'\("','',str(self.title))
						self.title = re.sub(r'\)', '', str(self.title))
						self.title = re.sub(r'"', '', str(self.title))
						self.title = re.sub(r';', '', str(self.title))
						self.title = re.sub(r'}', '', str(self.title))
						self.time = self.today
						# print(self.time)
						self.name_ch = self.soup.select("a[href='javascript:void(0);']")
						self.name_ch = re.sub(r'<[^>]+>', '', str(self.name_ch[0]))
						self.name_ch = re.sub(r'\\r','',str(self.name_ch))
						self.name_ch = re.sub(r'\s+','',str(self.name_ch))
						# print(self.name_ch)
						self.class_ = 'wechat'
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
					except:
						self.failed_link.append(self.address)
						print('Invalid link %s' %(self.address))
			self.daily_log('Wechat', self.t[-1], self.crawls, self.addins, self.fail,				self.failname,self.failed_link)

if __name__ == "__main__":
	sinaspider = WechatSpider()
	sinaspider.Json_pipeline()
	import sys
	sys.path.insert(0, '/home/daiym/new-spider-alpha/SVM_HEADLINE')
	import SVM_headline
	SVM_headline.SVM_headline().run_headline()
	import sys
	sys.path.insert(0, '/home/daiym/new-spider-alpha/Article_spider')
	import content_spider
	content_spider.Content_spider().save_article()