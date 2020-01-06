import os
import datetime
import shutil

class Screen(object):
    def __init__(self):
        self.max_steps = 1000
        self.filter_size = '2,3,4,5'

    def screen(self):

        past_date = str(datetime.datetime.now() + datetime.timedelta(-1))[:10]
        new_date = str(datetime.datetime.now())[:10]

        past_dir = './CNN_screen/runs/' + str(past_date)
        if os.path.isdir(past_dir) == True:
            shutil.rmtree(past_dir)

        from CNN_screen import getdata

        textT, textF, textTest, textID = getdata.data_collect().getdata(new_date)
        if textTest == 0:
            print('no test data available for evaluation')
            return

        print('checkpoint: getdata.py finished')

        from CNN_screen import eval as E
        today_dir = './CNN_screen/runs/' + str(new_date)

        if os.path.isdir(today_dir) == True:
            Screen_News = E.eval().eval_train(new_date,textTest, textID)
            print('checkpoint: eval.py finished')
        else:
            from CNN_screen import train
            Train = train.train().train(new_date, textT, textF, self.max_steps, self.filter_size)
            print('checkpoint: train.py finished')
            Screen_News = E.eval().eval_train(new_date,textTest, textID)
            print('checkpoint: eval.py finished')

if __name__ == "__main__":
    screen = Screen().screen()