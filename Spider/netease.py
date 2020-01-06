# coding=utf-8
import re
from Spider.spider import Spider
import urllib.request
import json


class NeteaseSpider(Spider):
	def __init__(self):
		super(NeteaseSpider, self).__init__('netease', "网易智能", "http://tech.163.com/special/00097UHL/smart_datalist.js?callback=data_callback", 'web')
		self.fail = 0

	def content_acquire(self):
		self.f = open('./netease-path.txt', 'r')
		for self.address in self.f:
			self.address = self.address[:-1]
			self.address = self.address.replace('\ufeff', '')
			self.response = urllib.request.urlopen(self.address)
			self.html = self.response.read()
			self.html = str(self.html,'gbk')
			self.html = re.sub(r'data_callback\(', '', str(self.html))
			self.html = re.sub(r'\)', '', self.html)
			self.items = json.loads(self.html)
			if self.items != []:
				for i in range(len(self.items)):
					self.item = self.items[i]
					self.title = self.item['title']
					self.time = self.decode(self.item['time'][:10])
					self.link = self.item['docurl']
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

		self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
							   self.failed_link)

	def decode(self,t):
		t = str(t)
		day = t[3:5]
		mth = t[:2]
		year = t[6:11]
		time = year +'-'+ mth +'-'+ day
		return(time)

if __name__ == "__main__":
	sinaspider = NeteaseSpider()
	sinaspider.Json_pipeline()