# coding=utf-8

import datetime
import time
from pymongo import MongoClient
import urllib.request
import Levenshtein as lst
import urllib
from dateutil import parser


def str2time(date):
	'''
    将2018-10-10这样的格式的日期转换为时间
    :param date: 日期，格式必须是"YYYY-MM-DD"
    :return: 时间格式
    '''
	datetime_struct = parser.parse(date)
	return datetime_struct

class Spider(object):
	def __init__(self, name, name_ch, address, class_):
		self.start_time = time.clock()
		self.fail = 0
		self.addins = 0
		self.crawls = 0
		self.failed_link = []
		self.failname = []
		self.t = datetime.datetime.now()
		self.t_1 = self.t
		# self.t = [str(self.t)[:10]] '2018-05-10'
		self.name = name
		self.class_ = class_
		self.name_ch = name_ch
		self.address = address
		self.tokenlist = ['36氪', '新浪科技', '网易智能', '亿欧', '雷锋网']
		host = ''
		port = ''
		user_name = ''
		user_pwd = ''
		db_name = ''
		uri = "mongodb://"+ user_name + ":" + user_pwd + "@" + host + ":" + port + "/" + db_name
		client = MongoClient(uri)
		self.db = client[db_name]
		time_now = self.db.times.find({})
		self.t = [i['time'] for i in time_now][0]
		self.t_delta = str(str2time(self.t) + datetime.timedelta(days=1))[:10]
		self.t = [str(self.t_1)[:10], str(self.t_delta)]
		self.month_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
		                   'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
						   'JANUARY': 1, 'FEBUARY': 2, 'MARCH': 3, 'APRIL': 4, 'JUNE': 6, 'JULY': 7,
						   'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12,
		                   'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7,
		                   'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
						   'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'Jun': 6, 'Jul': 7,
						   'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }

		self.header = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

	def getWeb(self):
		try:
			self.request = urllib.request.Request(url=self.address, headers=self.header)
			self.response = urllib.request.urlopen(self.request, timeout=20)
			self.html = str(self.response.read(), 'utf-8')
			self.fail = False
			return 1
		except:
			self.fail = True
			return 0

	def content_acquire(self):
		print("Not implemented")

	def cruiser_to_list(self,cruiser,keyname):
		result_list = [doc[str(keyname)] for doc in cruiser]
		return(result_list)

	def id_generator(self,list,value_keyname):
		valuelist = []
		for i in list:
			id = self.cruiser_to_list(self.db.NEWS.find({"title": str(i)}), value_keyname)
			valuelist.append(id[0])
		return valuelist

	def lst_result_generator(self,available,target_news):
		if lst.ratio(str(available.split()), str(target_news.split())) > 0.58:
			return str(available)
		else:
			return None

	def duplicate_id_generator(self,target_news,collection):
		simarticles = []
		for i in collection:
			result = self.lst_result_generator(str(i), target_news)
			if result != None:
				simarticles.append(result)

		if simarticles != []:
			simId = self.id_generator(simarticles,'_id')
			return simId
		else:
			return None

	def exist_detecter(self,newstitle):
		exist = self.db.NEWS.find({"title": newstitle}).count()
		if exist != 0:
			return 0
		else:
			return 1

	def anti_spider_alert(self,newstitle,date,spidername):
		if newstitle == '':
			return 1,spidername
		elif newstitle == []:
			return 1,spidername
		elif newstitle == ' ':
			return 1,spidername
		elif '{' in newstitle:
			return 1,spidername
		elif len(date) != 10:
			return 1,spidername
		else:
			return 0,spidername
		# discussion？

	def write(self,name_ch,title,time,link,class_):
		result,spidername = self.anti_spider_alert(title,time,name_ch)
		if result == 1:
			return 0
		else:
			if self.class_ == 'wechat':
				exist = self.db.NEWS.find({"$and": [{"title": title}, {"class": "wechat"}]}).count()
				if exist == 0:
					self.availables_wechat = self.cruiser_to_list(self.db.NEWS.find({'collect': True}), "title")
					self.simId = self.duplicate_id_generator(title, self.availables_wechat)
					del self.availables_wechat
					if self.simId == None:
						try:
							self.db.NEWS.insert_one({
								"source": name_ch, "coll_date": self.t[-1],
								"date": time, "title": title,
								"class": class_, "link": link,
								"screen": True, "collect": True})
							print('"%s" has successfully been saved' % str(title))
							return (1)
						except:
							return (0)

					else:
						print('"%s" has a similar article' % str(title))
						try:
							self.db.NEWS.insert_one({
								"source": name_ch, "coll_date": self.t[-1],
								"date": time, "title": title,
								"class": class_, "link": link,
								"screen": True, "collect": False, "sim_news": self.simId})
							return (2)
						except:
							return (0)

				else:
					print('"%s" exists' % str(title))
					return (2)

			else:
				if name_ch in self.tokenlist:
					exist = self.exist_detecter(title)
					if exist == 1:
						self.availables_web = self.cruiser_to_list(self.db.NEWS.find({}), "title")
						self.simId = self.duplicate_id_generator(title, self.availables_web)
						del self.availables_web
						if self.simId == None:
							try:
								self.db.NEWS.insert_one({
									"source": name_ch, "coll_date": self.t[-1],
									"date": time, "title": title,
									"class": class_, "link": link,
									"screen": False, "collect": False})
								print('"%s" has successfully been saved' % str(title))
								return (1)
							except:
								return (0)

						else:
							print('"%s" has a similar article' % str(title))
							try:
								self.db.NEWS.insert_one({
									"source": name_ch, "coll_date": self.t[-1],
									"date": time, "title": title,
									"class": class_, "link": link,
									"screen": True, "collect": False, "sim_news": self.simId})
								return (2)
							except:
								return (0)
					else:
						print('"%s" exists' % str(title))
						return (2)

				else:
					exist = self.exist_detecter(title)
					if exist == 1:
						try:
							self.db.NEWS.insert_one({
								"source": name_ch, "coll_date": self.t[-1],
								"date": time, "title": title,
								"class": class_, "link": link,
								"screen": False, "collect": False})
							print('"%s" has successfully been saved' % str(title))
							return (1)
						except:
							return (0)
					else:
						print('%s exits' % str(title))
						return (2)

	# def Email(self, to, subject, body):
		# creds = Credentials(
		# 	username='ai_news_notice@outlook.com',
		# 	password='2D2f4Z1993'
		# )
		# account = Account(
		# 	primary_smtp_address='ai_news_notice@outlook.com',
		# 	fullname='ai_news_notice@outlook.com',
		# 	credentials=creds,
		# 	autodiscover=True,
		# 	access_type=DELEGATE
		# )
		# m = Message(
		# 	account=account,
		# 	subject=subject,
		# 	body=HTMLBody(body),
		# 	to_recipients=[Mailbox(email_address=to)]
		# )
		# m.send()

	def daily_log(self,name_ch,coll_date,crawls,addins,failed,faillist,failedlink):
		self.end_time = time.clock()
		runtime = self.end_time - self.start_time
		self.db.DAILY_LOG.insert_one(
			{'spider': name_ch,'new_addins': addins,
			 'new_crawl': crawls,'running_date':str(datetime.datetime.now())[:19],
			 'running_time': runtime,'fail_title':faillist,'fail_link':failedlink})
		print('%s valid article(s)' % str(addins))
		# if self.failed_link != []:
		# 	text = '以下爬虫链接可能失效，请管理员查看:\n%s' %str(failedlink)
		# 	try:
		# 		self.Email('yiming.dai.1993@outlook.com','爬虫出现问题，请及时查看',text)
		# 		print('success')
		# 	except:
		# 		print('failed to send email')

	def Beautiful_pipeline(self):
		self.getWeb()
		flag = self.getWeb()
		if flag == 1:
			self.content_acquire()
		else:
			print('failed url, please try later')

	def Json_pipeline(self):
		self.content_acquire()
