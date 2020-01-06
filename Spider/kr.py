# coding='utf-8'
from Spider.spider import Spider
import urllib.request
import json



class KrSpider(Spider):
	def __init__(self):
		super(KrSpider, self).__init__('kr', "36氪", 'kr','web')
		self.fail = 0

	def content_acquire(self):
		self.f = open('./kr-path.txt', 'r')
		for self.address in self.f:
			self.address = self.address[:-1]
			self.address = self.address.replace('\ufeff', '')
			self.response = urllib.request.urlopen(self.address)
			self.html = self.response.read()
			self.html = json.loads(self.html)
			self.items = self.html['data']['items']
			for i in range(len(self.items)):
				if self.items[i] != []:
					self.item = self.items[i]
					self.title = self.item['title']
					self.time = self.item['published_at'][:10]
					self.link = "http://36kr.com/p/" + str(self.item['id']) + ".html"
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
	sinaspider = KrSpider()
	sinaspider.Json_pipeline()