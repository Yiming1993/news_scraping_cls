# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider


class WiredSpider(Spider):
	def __init__(self):
		super(WiredSpider, self).__init__('wired', "WIRED", "https://www.wired.com/category/science/page/1/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html, 'lxml')
		self.news = self.soup.select("li[class='archive-item-component']")

		for i in range(len(self.news)):
			try:
				self.new = self.news[i]
				if self.new.select("h2[class='archive-item-component__title']") != []:
					self.title = self.new.select("h2[class='archive-item-component__title']")[-1]
					self.title = re.sub(r'<[^>]+>', '', str(self.title))
					# print(self.title)
					if self.new.select("time") != []:
						self.time = self.new.select("time")
						self.time = re.sub(r'<[^>]+>', '', str(self.time[-1]))
						self.time = self.decode(self.time)
						# print(self.time)
						if self.new.select("a[class='archive-item-component__link']") !=[]:
							self.link = self.new.select("a[class='archive-item-component__link']")
							self.link = re.findall(r'/story/[^>]+/', str(self.link))
							self.link = re.sub(r'to=[^>+]','',str(self.link[0]))
							self.link = re.split('"',self.link)
							self.link = self.link[0]
							if self.link != []:
								self.link = 'https://www.wired.com' + str(self.link)
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
			except:
				continue

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
		if year == '':
			year = data
		time = year + '-' + mth + '-' + day
		return time


if __name__ == "__main__":
	sinaspider = WiredSpider()
	sinaspider.Beautiful_pipeline()
