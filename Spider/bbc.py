# coding=utf-8
from Spider.spider import Spider
from bs4 import BeautifulSoup
import re


# import simhash


class BbcSpider(Spider):
	def __init__(self):
		super(BbcSpider, self).__init__('bbc', "BBC", "http://www.bbc.com/news/technology", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html, 'lxml')
		self.news = self.soup.select("div")
		for self.new in self.news:
			self.title = self.new.select("span[class='title-link__title-text']")
			if self.title != []:
				self.title = re.sub(r'<[^>]+>', '', str(self.title[0]))
				# print(self.title)
				self.time = self.new.select("ul[class='mini-info-list'] div[class='date date--v2']")
				if self.time != []:
					self.time = re.sub(r'<[^>]+>', '', str(self.time[0]))
					self.link = self.new.select("a[class='title-link']")
					self.link = re.findall(r'href="[^>]+"', str(self.link[0]))
					self.link = re.sub(r'href="','',str(self.link[0]))
					self.link = re.sub(r'"','',str(self.link))
					if self.link[0] != 'h':
						self.link = 'http://www.bbc.co.uk' + self.link
						# print(self.link)
						self.time = self.decode(self.time)
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

		self.daily_log(self.name_ch,self.t[-1],self.crawls,self.addins,self.fail,self.failname,self.failed_link)


	def decode(self, t):
		t = str(t)
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
	sinaspider = BbcSpider()
	sinaspider.Beautiful_pipeline()

