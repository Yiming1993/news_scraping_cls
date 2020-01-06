# coding=utf-8
# reload(sys)
# python默认环境编码时ascii
import datetime

#from urllib import quote_plus
spiders_to_wrote = ['kr', 'sina', 'netease', 'cbs', 'techcrunch', 'techrepublic', 'wired', 'zdnet']
#from wechat import WechatSpider
from Spider.spider import Spider



def process_line(line):
	part = ''
	s = ''  # source of the news
	t = ''  # title of the news
	l = ''  # link of the news

	for letter in line:
		if s == '':
			if letter != '|':
				part += letter
			else:
				s = part
				part = ''
		elif t == '':
			if ((part[-8:] != 'https://') & (part[-7:] != 'http://')):
				part += letter
			else:

				if part[-8:] == 'https://':
					t = part[:-8]
					part = 'https://' + letter
				else:
					t = part[:-7]
					part = 'http://' + letter
		else:
			part += letter
	l = part[:-1]
	return s, t, l


def select_write_from_db(db, path):

	cursor = db.NEWS_171127.find({"screen": False})
	# cursor = db.NEWS.find({"coll_date": "2017-06-05"})
	i = 0
	id_seq = []
	for doc in cursor:
		print(i, doc['source']+'|'+doc['title']+' '+doc['link'])
		id_seq.append(doc['_id'])
		i += 1
	if i > 0:
		# get selected news
		a = input('select news：')
		# process a and get int sequence
		select = []
		num = ''
		j = 0
		if a != '':
			while j < len(a):
				if ((j == 0) & (a[0] == '\n')):
					break
				if a[j] != ',':
					num += a[j]
				else:
					select.append(int(num))
					num = ''
				j += 1
			select.append(int(num))
		# write collected news in a txt file and modify their 'collect' property in the database
		f = open(path + 'collect_news.txt', 'a')
		for sel_num in select:
			id = id_seq[sel_num]
			db.NEWS_171127.update({"_id": id}, {"$set": {"collect": True}})
			cursor = db.NEWS_171127.find({"_id": id})
			for doc in cursor:
				print(f, doc['source']+'|'+doc['title']+' '+doc['link'])
		f.close()
		db.NEWS_171127.update({}, {"$set": {"screen": True}}, multi=True)
	pass


def select_write(news_file, path, select, filename,index_start,m, t):


	contents = []
	select = path + select

	for line in open(select + '.txt'):
		contents.append(line)
	# write the results
	print_quant = 10
	select = []
	num = ''
	j = 0
	contents = contents[m][1:-2] + '\n'
	while j < (len(contents)-1):

		if ((j == 0)&(contents[0]=='\n')):
			break
		if contents[j] != ',':
			num += contents[j]
		else:
			select.append(int(num))
			num = ''
		j += 1
	select.append(int(num))

	contents = []
	for line in open(path + news_file + '.txt'):
		contents.append(line)

	with open(path + filename, 'wb') as f:
		for j in range(len(select)):
			ind = select[j]-1
			s, t, l = process_line(contents[ind])
			db.NEWS_171127.update({"link": l}, {"$set": {"collect": True}})
			print(f, contents[ind][:-1])

	return index_start + len(select)


def collect_all_news(name_set):
	f = open(path + 'all_news.txt', 'wb')

	for name in name_set:
		j = 1
		for line in open(path + name + '.txt'):
			if j < 10:
				print >> f, line[:-1]
				# print >> f, str(index_start + j) + '. ' + contents[ind][3:-1]
			else:
				print >> f, line[:-1]
			j += 1


if __name__ == "__main__":
	now = datetime.datetime.now()
	t = now.strftime('%Y-%m-%d %H:%M:%S')[:10]
	path = './news/' + str(t[:10]) + '/'
	spider_base = Spider('', '', '', '')


	spiders_to_soup_json = [
		"Wechat"
	]

	failed_set = []
	running_spider = eval('WechatSpider()')
	flag, failname = running_spider.Json_pipeline()
	if flag != '1':
		failed_set = failname
	print("Failed sets: ", failed_set)

