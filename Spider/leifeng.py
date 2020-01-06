# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup


# import simhash


class LeifengSpider(Spider):
	def __init__(self):
		super(LeifengSpider, self).__init__('leifeng', "雷锋网", "http://www.leiphone.com", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		if self.soup.select("div[class='box'] div[class='word'] h3 a") !=[]:
			self.news = self.soup.select("div[class='box'] div[class='word'] h3 a")
			for i in range(len(self.news)):
				self.new = self.news[i]
				self.title = re.sub(r'<[^>]+>','',str(self.new))
				self.title = re.sub(r'\s+','',str(self.title))
				self.link = re.findall(r'www.leiphone.com/news/[^>]+',str(self.new))
				if self.link !=[]:
					self.link = 'http://' + re.split('["\s]',str(self.link[-1]))[0]
					self.time = self.t[0]
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

if __name__ == "__main__":
	sinaspider = LeifengSpider()
	sinaspider.Beautiful_pipeline()
