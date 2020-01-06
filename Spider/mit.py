# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup


class MitSpider(Spider):
	def __init__(self):
		super(MitSpider, self).__init__('mit', "MIT Technology Review", "https://www.technologyreview.com/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.tops = self.soup.select("div[class='cover-tz__img-mod']")
		self.topstories = self.soup.select("div[class='top-stories'] article[class='top-story']")
		self.ordinarys = self.soup.select("div[class='grid-tz grid-tz--img']")

		for i in range(len(self.tops)):
			self.top = self.tops[i]
			if self.top.select("a h2[class='hp-lead__title']") !=[]:
				self.title = self.top.select("a h2[class='hp-lead__title']")
				self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
				if self.top.select("a") !=[]:
					self.link = self.top.select("a")
					self.link = re.findall(r'/s/[^>]+/',str(self.link[0]))
					if self.link != []:
						self.link = "https://www.technologyreview.com" +self.link[0]
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


		for i in range(len(self.topstories)):
			self.topstory = self.topstories[i]
			if self.topstory.select("a h2[class='top-story__title']") !=[]:
				self.title = self.topstory.select("a h2[class='top-story__title']")
				self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
				if self.topstory.select("a") !=[]:
					self.link = self.topstory.select("a")
					self.link = re.findall(r'/s/[^>]+/',str(self.link[0]))
					if self.link !=[]:
						self.link = "https://www.technologyreview.com" + self.link[0]
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

		for i in range(len(self.ordinarys)):
			self.ordinary = self.ordinarys[i]
			if self.ordinary.select("h2[class='grid-tz__title'] a") !=[]:
				self.title = self.ordinary.select("h2[class='grid-tz__title'] a")
				self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
				if self.ordinary.select("h2[class='grid-tz__title'] a") !=[]:
					self.link = self.ordinary.select("h2[class='grid-tz__title'] a")
					self.link = re.findall(r'/s/[^>]+/',str(self.link[0]))
					if self.link !=[]:
						self.link = "https://www.technologyreview.com" + str(self.link[0])
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
	sinaspider = MitSpider()
	sinaspider.Beautiful_pipeline()