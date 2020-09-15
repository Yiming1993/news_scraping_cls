import smtplib
from email.mime.text import MIMEText
from email.header import Header
from time import time,localtime,strftime
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from email.mime.multipart import MIMEMultipart
import datetime
import os
from Spider.spider import Spider

class Alert(Spider):
    def __init__(self):
        super(Alert,self).__init__('email','email','email','email')
        self.weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        self.mail_list = [
                           ]
        self.name_list = []

    def Email(self, to, subject, body):
        mail_host = "smtp.139.com"
        mail_user = ""
        mail_pass = ""
        sender = ""

        message = MIMEMultipart()
        message['From'] = Header(sender,'utf-8')
        message['To'] = Header(to, 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        # att1 = MIMEText(open('./headline_today.txt', 'rb').read(), 'base64', 'utf-8')
        # att1["Content-Type"] = 'application/octet-stream'
        # att1["Content-Disposition"] = 'attachment; filename="headline_today.txt"'
        # message.attach(att1)
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host,25)
        # smtpObj.ehlo()
        # smtpObj.starttls()
        # smtpObj.set_debuglevel(1)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, [to], message.as_string())
        print('Email sent to %s' % to)
        # except:
        #     admin = ''
        #     message = MIMEMultipart()
        #     message['From'] = Header(sender, 'utf-8')
        #     message['To'] = Header(admin, 'utf-8')
        #     message['Subject'] = Header('邮件系统故障', 'utf-8')
        #     message.attach(MIMEText(body, 'plain', 'utf-8'))
        #     att1 = MIMEText(open('./headline_today.txt', 'rb').read(), 'base64', 'utf-8')
        #     att1["Content-Type"] = 'application/octet-stream'
        #     att1["Content-Disposition"] = 'attachment; filename="headline_today.txt"'
        #     message.attach(att1)
        #     smtpObj = smtplib.SMTP(mail_host,25)
        #     smtpObj.starttls()
        #     # smtpObj.set_debuglevel(1)
        #     # smtpObj.ehlo()
        #     # smtpObj.starttls()
        #     smtpObj.login(mail_user, mail_pass)
        #     smtpObj.sendmail(sender, admin, message.as_string())
        #     print('Email sent to admin %s' % admin)

    def work_check(self,to,subject,body):
        news = self.db.NEWS.find({"$and":[{"coll_date":self.t[-1]},{"collect":True}]})
        news_coll = [doc["title"] for doc in news]
        if news_coll == []:
            self.Email(to,subject,body)
        else:
            pass

    def get_headline(self):
        if os.path.isfile('./headline_today.txt') == True:
            os.remove('./headline_today.txt')
        today = str(datetime.datetime.now())[:10]
        headline = self.db.NEWS.find({"coll_date":today})
        rank = {}
        for i in headline:
            try:
                rank[i["title"]] = i["hd_score"]
            except:
                pass
        final_rank = sorted(rank.items(),key=lambda x:x[1],reverse=True)
        for i in final_rank:
            f = open('./headline_today.txt', 'a')
            f.write(str(i)+'\n')
            f.close()

    def get_weekday(self):
        x = localtime(time())
        return strftime("%A", x)

    def daily_notice(self):
        mail_list = list(zip(self.name_list, self.mail_list))
        today = self.get_weekday()
        name_list = list(zip(self.weekdays, mail_list))
        self.get_headline()
        for i in name_list:
            if today == i[0]:
                mail_address = i[1][1]
                # print(mail_address)
                text = str(i[1][0]) + ''
                self.Email(mail_address, '', text)
                break
            else:
                continue

    def delay_notice(self):
        mail_list = list(zip(self.name_list, self.mail_list))
        today = self.get_weekday()
        name_list = list(zip(self.weekdays, mail_list))
        # self.get_headline()
        f = open('./headline_today.txt', 'a')
        f.write('' + '\n')
        f.close()
        for i in name_list:
            if today == i[0]:
                mail_address = i[1][1]
                # print(mail_address)
                text = str(i[1][0]) + ''
                self.work_check(mail_address, '', text)
                break
            else:
                continue

if __name__ == '__main__':
    E = Alert()
    E.delay_notice()
