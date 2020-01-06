# coding=utf-8

import re

from bs4 import BeautifulSoup
from Spider.spider import Spider

class YiouSpider(Spider):
	def __init__(self):
		super(YiouSpider, self).__init__('yiou', "亿欧", "http://www.iyiou.com", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.lists = self.soup.select("li a")
		for i in range(len(self.lists)):
			self.list = self.lists[i]
			self.title = str(self.list.string)
			self.link = re.findall(r'/p/[0-9]{1,5}',str(self.list))
			if self.title != 'None':
				if self.link != []:
					self.link = 'http://www.iyiou.com' + self.link[-1]
					self.time = self.t[0]
					state = self.write(self.name_ch,self.title,self.time,self.link,self.class_)
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

if __name__ == "__main__":
	sinaspider = YiouSpider()
	sinaspider.Beautiful_pipeline()
