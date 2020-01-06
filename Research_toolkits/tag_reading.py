import re
from Research_toolkits import label_reading

f = open('tags_pred.txt','r').readlines()
iterT = 0
newst = 0
counterColl = {}
news_title = []
data_matrix = []
while iterT <= 2261:
    newst += 1
    if iterT % 2 !=0:
        num = f[iterT][22:]
        num = re.sub(r'\n','',str(num))
        num = int(num)
        news = re.sub(r'\n','',str(f[iterT-1]))
        counterColl[news] = num

        iterT += 1
    else:
        iterT += 1
        pass

news_tags = sorted(counterColl.items(), key=lambda x: x[1], reverse=False)
# print(news_tags)
# count = 0
# for i in news_tags:
#     news_title.append(count)
#     data_matrix.append(i[1])
#     count+=1
# plt.figure()
# plt.bar(news_title,np.array(data_matrix))
# plt.xlabel('news number')
# plt.ylabel('num_tags')
# plt.show()
high_tag = news_tags[-100:]
origin_tags = [label_reading.label_reading().label_search_single_news(str(i[0])) for i in high_tag]
final_result = list(zip(high_tag,origin_tags))
print(final_result)