# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider



class ZdnetSpider(Spider):
	def __init__(self):
		super(ZdnetSpider, self).__init__('zdnet', "ZDNet", "http://www.zdnet.com/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.rollings = self.soup.select("section")
		self.fixing1s = self.soup.select("article[class='item']")
		self.fixing2s = self.soup.select("ul li")
		for i in range(len(self.rollings)):
			try:
				self.rolling = self.rollings[i]
				if self.rolling.select("h3[class='title'] a") !=[]:
					self.title = self.rolling.select("h3[class='title'] a")
					self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
					self.time = self.t[-1]
					if self.rolling.select("h3[class='title'] a") !=[]:
						self.link = self.rolling.select("h3[class='title'] a")
						if self.link != []:
							self.link = re.findall(r'/article/[^>]+/',str(self.link[-1]))
							if self.link !=[]:
								self.link = "http://www.zdnet.com" +self.link[0]
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
				continue

		for i in range(len(self.fixing1s)):
			try:
				self.fix1 = self.fixing1s[i]
				if self.fix1.select("h3 a") !=[]:
					self.title = self.fix1.select("h3 a")
					self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
					if self.fix1.select("p[class='meta'] span") !=[]:
						self.time = self.t[-1]
						if self.fix1.select("h3 a") !=[]:
							self.link = self.fix1.select("h3 a")
							self.link = re.findall(r'/article/[^>]+/',str(self.link[-1]))
							if self.link !=[]:
								self.link = "http://www.zdnet.com" + self.link[0]
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
				continue
			for i in range(len(self.fixing2s)):
				try:
					self.fix2 = self.fixing2s[i]
					if self.fix2.select("div[class='content'] a") !=[]:
						self.title = self.fix2.select("div[class='content'] a")
						self.title = re.sub(r'<[^>]+>\s+','',str(self.title[-1]))
						self.title = re.sub(r'\s+</a>','',self.title)
						if self.fix2.select("div[class='meta'] span") !=[]:
							self.time = self.t[-1]
							if self.fix2.select("div[class='content'] a") !=[]:
								self.link = self.fix2.select("div[class='content'] a")
								self.link = re.findall(r'/article/[^>]+/',str(self.link[-1]))
								if self.link !=[]:
									self.link = "http://www.zdnet.com" + self.link[0]
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
					continue
		self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
									   self.failed_link)

if __name__ == "__main__":
	sinaspider = ZdnetSpider()
	sinaspider.Beautiful_pipeline()
