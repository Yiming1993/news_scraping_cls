# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup

class FuturismSpider(Spider):
	def __init__(self):
		super(FuturismSpider, self).__init__('futurism', "Futurism", "https://futurism.com/artificialintelligence/", 'web')
		self.t_stamp = self.t

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html,'lxml')
		self.stories = self.soup.select("div[class='Stories'] a")
		for i in range(len(self.stories)):
			self.title = self.stories[i].select("h4")[-1]
			self.title = re.sub(r'<[^>]+>\s+','',str(self.title))
			self.title = re.sub(r'\s+</a>','',str(self.title))
			self.title = re.sub(r'<[^>]+>','',str(self.title))
			self.link = re.findall(r'href=[^>]+', str(self.stories[i]))
			if self.link != []:
				self.link = self.link[0]
				self.link = re.sub(r'href="','﻿﻿﻿﻿﻿https://futurism.com', str(self.link))
				self.link = re.sub(r'"', '', str(self.link))
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

	def decode(self, t):
		t = str(t)
		if t[-3:] == 'ago':
			return self.t[-1]
		else:
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
			if (year == '')&(data !=''):
				year = data
			time = year + '-' + mth + '-' + day
			return time

if __name__ == "__main__":

	sinaspider = FuturismSpider()
	sinaspider.Beautiful_pipeline()
