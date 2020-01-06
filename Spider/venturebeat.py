# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider


class VenturebeatSpider(Spider):
	def __init__(self):
		super(VenturebeatSpider, self).__init__('venturebeat', "VentureBeat", "https://venturebeat.com/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.news = self.soup.select("header[class='article-header']")
		for i in range(len(self.news)):
			self.new = self.news[i]
			if self.new.select("h2[class='article-title'] a") != []:
				self.title = self.new.select("h2[class='article-title'] a")[-1]
				self.title = re.sub(r'<[^>]+>', '', str(self.title))
				if self.new.select("div[class='article-byline'] a") != []:
					self.time = self.new.select("div[class='article-byline'] time")
					self.time = re.findall(r'title="[^>]+"',str(self.time[-1]))
					self.time = re.sub(r'title="','',str(self.time[-1]))
					self.time = self.time[:10]
					if self.new.select("h2[class='article-title'] a") !=[]:
						self.link = self.new.select("h2[class='article-title'] a")
						self.link = re.findall(r'venturebeat.com/[^>]+/', str(self.link))
						if self.link != []:
							self.link = 'https://www.' + str(self.link[-1])
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
		t = str(t)[:-9]
		data = ''
		mth = ''
		day = ''
		year = ''
		for i in range(len(t)):
			if t[i] not in [' ', ',']:
				data += t[i]
			elif data != '':
				if day == '':
					day = data
					if len(data) <2:
						day = '0' + data
				elif mth == '':
					mth = str(self.month_dict[data])
					if len(mth) <2:
						mth = '0' + mth
				elif year == '':
					year = data
					break
				data = ''
		if (data != '')&(year==''):
			year = data
		time = year + '-' + mth + '-' + day
		return time

if __name__ == "__main__":
	sinaspider = VenturebeatSpider()
	sinaspider.Beautiful_pipeline()

