# coding=utf-8
import re

from bs4 import BeautifulSoup
from Spider.spider import Spider



class TrSpider(Spider):
	def __init__(self):
		super(TrSpider, self).__init__('techrepublic', "TechRepublic", "https://www.techrepublic.com",'web')


	def content_acquire(self):
		self.soup = BeautifulSoup(self.html, 'lxml')
		self.news = self.soup.select("ul[class='media-list items'] li")
		for i in range(len(self.news)):
			self.new = self.news[i]
			if self.new.select("h3[class='title'] a") != []:
				self.title = self.new.select("h3[class='title'] a")[-1]
				self.title = re.sub(r'<[^>]+>', '', str(self.title))
				if self.new.select("p[class='meta'] span[class='separator']") !=[]:
					self.time = self.new.select("p[class='meta']")
					self.time = re.findall(r'</span>[^>]+</p>', str(self.time))
					self.time = re.sub(r'<[^>]+>','',str(self.time))
					self.time = re.sub(r'\\n','',str(self.time))
					self.time = re.sub(r'\\t','',str(self.time))
					self.time = re.findall(r"'[^>]+'", self.time)[-1]
					self.time = self.decode(self.time)
					if self.new.select("h3[class='title'] a") !=[]:
						self.link = self.new.select("h3[class='title'] a")
						self.link = re.findall(r'www.techrepublic.com/[^>]+', str(self.link))
						if self.link != []:
							self.link = 'https://' + re.split('["\s]', str(self.link[-1]))[0]
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
		start = t.find('·')
		data = ''
		mth = ''
		day = ''
		year = ''
		t = t[start+2:]
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

	sinaspider = TrSpider()
	sinaspider.Beautiful_pipeline()