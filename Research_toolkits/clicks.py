from SVM_SCREEN.SVM_screen import SVM_screen

class clicks(SVM_screen):
    def __init__(self):
        super(clicks,self).__init__()
        self.test_date = ''

    def get_clicks(self):
        click_news = {}
        news = self.db.NEWS.find({"clicks":{"$exists":True}})
        dict = [i for i in news]
        for doc in dict:
            click_news[doc["title"]] = doc["clicks"]
        clicks = sorted(click_news.items(),key=lambda x:x[1],reverse=True)
        print(clicks)

    def get_clicks_test(self):
        y_test = []
        news = self.db.NEWS.find({"$and":[{"collect":True},{"coll_date":self.test_date}]})
        x_test = [doc["title"] for doc in news]
        for doc in news:
            y_test.append(doc["clicks"])

        return x_test, y_test

if __name__ == "__main__":
    C = clicks()
    C.get_clicks_test()
