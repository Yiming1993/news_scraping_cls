# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider


class AtlanticSpider(Spider):
	def __init__(self):
		super(AtlanticSpider, self).__init__('theatlantic', "The Atlantic", "https://www.theatlantic.com/technology/",'web')
	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.news = self.soup.select("li[class='article blog-article ']")
		for self.new in self.news:
			self.title = self.new.select("h2[class='hed']")
			self.title = re.sub(r'<[^>]+>','',str(self.title[0]))
			self.link = self.new.select("a[data-omni-click='inherit']")
			self.link = re.findall(r'href="[^>]+"',str(self.link))
			self.link = re.sub(r'href="','',str(self.link[0]))
			self.link = re.sub(r'"','',self.link)
			self.link = 'https://www.theatlantic.com'+self.link
			# print(self.link)
			self.time = self.soup.select("li[class='date'] time")
			self.time = re.findall(r'datetime="[^>]+"',str(self.time))
			self.time = re.sub(r'datetime="','',str(self.time[0]))
			self.time = re.sub(r'"','',self.time)
			# print(self.link)
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
	sinaspider = AtlanticSpider()
	sinaspider.Beautiful_pipeline()
