import numpy as np
import re
from CNN_screen import seg_data


def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def load_data_and_labels(positive_data_file, negative_data_file):
    positive_examples = []
    for m in positive_data_file:
        m = seg_data.seg_sentence(m)
        positive_examples.append(m)
    for m in positive_examples:
        if m != '\s':
            if m != '':
                positive_examples = [s.strip() for s in positive_examples]

    negative_examples = []
    for m in negative_data_file:
        m = seg_data.seg_sentence(m)
        negative_examples.append(m)
    for m in negative_examples:
        if m != '\s':
            if m != '':
                negative_examples = [s.strip() for s in negative_examples]

    x_text = positive_examples + negative_examples
    # x_text = [clean_str(sent) for sent in x_text]
    positive_labels = [[0,1] for _ in positive_examples]
    negative_labels = [[1,0] for _ in negative_examples]
    y = np.concatenate([positive_labels,negative_labels],0)
    return[x_text,y]

def load_data_and_labels_screen(examples_pre):
    examples = []

    for m in examples_pre:
        m = seg_data.seg_sentence(m)
        examples.append(m)
    for m in examples:
        if m != '\s':
            if m != '':
                examples = [s.strip() for s in examples]

    x_text = examples
    return x_text

def load_data_and_labels_eval_screen(data_file):
    examples = data_file
    for m in examples:
        if m != '\s':
            if m != '':
                examples = [s.strip() for s in examples]

    x_text = examples
    return x_text

def batch_iter(data, batch_size, num_epochs, shuffle=True):
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        if shuffle:
            shuffle_indecs = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indecs]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num*batch_size
            end_index = min((batch_num+1)*batch_size,data_size)
            yield shuffled_data[start_index:end_index]