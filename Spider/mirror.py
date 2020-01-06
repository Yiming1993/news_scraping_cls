# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup


class MirrorSpider(Spider):
	def __init__(self):
		super(MirrorSpider, self).__init__('mirror', "Mirror", "http://www.mirror.co.uk/tech/", 'web')


	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.news = self.soup.select("div")
		for i in range(len(self.news)):
			self.new = self.news[i]
			if self.new.select("a[class='headline']") !=[]:
				self.title = self.new.select("a[class='headline']")
				self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
				self.link = re.findall(r'www.mirror.co.uk/tech/[^>]+',str(self.new.select("a[class='headline']")))
				if self.link !=[]:
					self.link = re.split('"', str(self.link[-1]))
					self.link = 'http://'+self.link[0]
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
	sinaspider = MirrorSpider()
	sinaspider.Beautiful_pipeline()

