# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup


class SpectrumSpider(Spider):
	def __init__(self):
		super(SpectrumSpider, self).__init__('spectrum', "IEEE Spectrum", "https://spectrum.ieee.org/getGlobalNavData", 'web')


	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.news = self.soup.select("article")
		for i in range(len(self.news)):
			self.new = self.news[i]
			if self.new.select("h6") !=[]:
				self.title = self.new.select("h6")
				self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
				if self.new.select("time") !=[]:
					self.time = self.new.select("time")
					self.time = re.sub(r'<[^>]+>','',str(self.time[-1]))
					if self.new.select("a") !=[]:
						self.link = self.new.select("a")
						self.link = re.findall(r'href=[^>]+',str(self.link[-1]))
						self.link = re.sub(r'href="','',str(self.link[-1]))
						if self.link !=[]:
							self.link = re.split('"',self.link)
							self.link = "https://spectrum.ieee.org" + self.link[0]
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

		self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
									   self.failed_link)

	def decode(self, t):
		t = str(t)
		t = re.sub(r'\xa0',' ',t)
		data = ''
		mth = ''
		day = ''
		year = self.t[-1][:4]
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
				data = ''
		if mth == '':
			mth = str(self.month_dict[data])
			if len(mth) < 2:
				mth = '0' + mth
		time = year + '-' + mth + '-' + day
		return time

if __name__ == "__main__":
	sinaspider = SpectrumSpider()
	sinaspider.Beautiful_pipeline()
