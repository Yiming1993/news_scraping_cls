import jieba

def seg_sentence(sentence):
    jieba.load_userdict('./References/dict.txt')
    stopwords = [line.strip() for line in open('./References/stop.txt', 'r', encoding='utf-8').readlines()]
    sentence_seged = jieba.cut(sentence.strip())
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                if word != '':
                    if word != ' ':
                        if word != '\xa0':
                            if len(word) > 1:
                                outstr += word
                                outstr += " "
    return outstr