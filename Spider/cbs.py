# coding=utf-8
import re
from bs4 import BeautifulSoup
from Spider.spider import Spider


class CbsSpider(Spider):
	def __init__(self):
		super(CbsSpider, self).__init__('cbs', "CBS", "http://www.cbsnews.com/latest/tech/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.news = self.soup.select("ul[class='items'] li")

		for i in range(len(self.news)):
			self.new = self.news[i]
			if self.new.select("a h3[class=title]") != []:
				self.title = self.new.select("a h3[class=title]")[-1]
				self.title = re.sub(r'<[^>]+>','',str(self.title))
				if self.new.select("div[class='media-body'] p[class='meta'] a span[class='date']") != []:
					self.time = self.new.select("div[class='media-body'] p[class='meta'] a span[class='date']")[-1]
					self.time = re.sub(r'<[^>]+>', '', str(self.time))
					self.time = self.decode(self.time)
					if self.new.select("div[class='media-body'] a") !=[]:
						self.link = self.new.select("div[class='media-body'] a")
						self.link = re.findall(r'/news/[^>]+/',str(self.link))
						if self.link != []:
							self.link = 'http://cbsnews.com' + self.link[0]
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

	def decode(self, t):
		data = ''
		mth = ''
		day = ''
		year = ''
		for i in range(len(t)):
			if t[i] not in [' ', ',']:
				data += t[i]
			elif data != '':
				if mth == '':
					mth = str(self.month_dict[data])
					if len(mth) <2:
						mth = '0' + mth
				elif day == '':
					day = data
					if len(data) <2:
						day = '0' + data
				elif year == '':
					year = data
					break
				data = ''
		time = year + '-' + mth + '-' + day
		return time

if __name__ == "__main__":

	sinaspider = CbsSpider()
	sinaspider.Beautiful_pipeline()

