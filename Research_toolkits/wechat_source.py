from Spider.spider import Spider

class get_wechat(Spider):
    def __init__(self):
        super(get_wechat,self).__init__('web','web','web','wec')
        self.source_pool = []

    def get_wechat(self):
        source = self.db.NEWS.find({"class":"wechat"})
        dict = [doc for doc in source]
        for i in dict:
            if i["source"] not in self.source_pool:
                self.source_pool.append(i["source"])
                print(i["source"])
            else:
                pass

        return self.source_pool

    def save_wechat(self):
        for i in self.source_pool:
            self.db.WECHAT_LIST.insert_one({"source_name":str(i)})
        print('all wechat names are saved')

if __name__ == "__main__":
    W = get_wechat()
    W.get_wechat()
    W.save_wechat()