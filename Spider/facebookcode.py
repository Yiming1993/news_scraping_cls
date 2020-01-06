#coding = 'utf-8'

from Spider.spider import Spider
from bs4 import BeautifulSoup
import re
import datetime

class CodefbSpider(Spider):
    def __init__(self):
        super(CodefbSpider, self).__init__('fb_code', "Facebook_Code", "https://code.fb.com", 'web')

    def content_acquire(self):
        soup = BeautifulSoup(self.html,'lxml')
        articles = soup.select('article div[class="entry-title"] a')
        for i in articles:
            title = re.sub(r'<[^>]+>','',str(i))
            self.title = re.sub(r'\s{2,}','',str(title))
            link = re.findall(r'href=[^>]+rel',str(i))[0]
            self.link = link[6:-5]
            self.time = str(datetime.datetime.now() - datetime.timedelta(days=1))[:10]
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

if __name__ == '__main__':
    sinaspider = Codefb()
    sinaspider.Beautiful_pipeline()