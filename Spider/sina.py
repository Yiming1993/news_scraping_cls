# coding=utf-8
import re
from Spider.spider import Spider
from bs4 import BeautifulSoup


class SinaSpider(Spider):
	def __init__(self):
		super(SinaSpider, self).__init__('sina', "新浪科技", "http://tech.sina.com.cn/", 'web')

	def content_acquire(self):
		self.soup = BeautifulSoup(self.html, 'lxml')
		self.news = self.soup.select("ul[class='seo_data_list'] li")
		for i in range(len(self.news)):
			if i < 150:
				self.new = self.news[i]
				if self.new.select("a[target='_blank']") != []:
					self.title = self.new.select("a[target='_blank']")
					self.title = re.sub(r'<[^>]+>','',str(self.title[-1]))
					self.time = self.t[0]
					if self.new.select("a[target='_blank']") != []:
						self.link = self.new.select("a[target='_blank']")
						self.link = re.findall(r'http://tech.sina.com.cn/[^>]+',str(self.link[-1]))
						if self.link !=[]:
							self.link = re.sub(r'\starget="_blank"','',self.link[-1])
							self.link = re.split('"',self.link)
							self.link = self.link[0]
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
			else:
				break
		self.daily_log(self.name_ch, self.t[-1], self.crawls, self.addins, self.fail, self.failname,
					   self.failed_link)

if __name__ == "__main__":
	sinaspider = SinaSpider()
	sinaspider.Beautiful_pipeline()

