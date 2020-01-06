# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider



class TcSpider(Spider):
	def __init__(self):
		super(TcSpider, self).__init__('techcrunch', "TechCrunch", "https://techcrunch.com/artificial-intelligence-2/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html, 'lxml')
		self.news = self.soup.select('a[class="post-block__title__link"]')
		for i in range(len(self.news)):
			self.title = self.news[i]
			self.title = re.sub(r'<[^>]+>','', str(self.title))
			self.title = re.sub(r'\xa0','', str(self.title))
			self.title = re.sub(r'\s{2,}', '', str(self.title))
			self.links = re.findall(r'href="[^>]+"', str(self.news[i]))
			for self.link in self.links:
				self.link = re.sub(r'href="','',str(self.link))
				self.link = re.sub(r'"','',self.link)
			if self.soup.select("time[class='river-byline__time']") !=[]:
				self.times = self.soup.select("time[class='river-byline__time']")
				self.times = re.findall(r'datetime="[^>]+"', str(self.times[-1]))
				self.time = re.sub(r'datetime="','',str(self.times[0]))
				self.time = self.time[:-16]
				print(self.title)
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
	sinaspider = TcSpider()
	sinaspider.Beautiful_pipeline()
