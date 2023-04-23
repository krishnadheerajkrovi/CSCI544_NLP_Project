#Importing libraries
import stanza
import numpy as np
import pandas as pd
from tqdm import tqdm


# Importing bad words vocabulary from csv
def get_bad_words(path):
    bad_words=[]
    with open(path) as f:
        for line in f.readlines():
            bad_words.append(line.split('\n')[0])
    return bad_words

#Get the sentences and their POS tags
def get_sentences_postags(dataset):
    # Importing Stanza POS tagger
    pos_tagger = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos',use_gpu=True)
    sentences = []
    pos_tags_dataset = []
    for sentence in tqdm(dataset.iloc[:,1].values.tolist()):
        doc = pos_tagger(sentence)
        pos_tags_dataset.append([word.xpos for sent in doc.sentences for word in sent.words])
        sentences.append([word.text for sent in doc.sentences for word in sent.words])
    return sentences,pos_tags_dataset


# Labelling the dataset
def label_dataset(sentences,bad_words_set):
    labels = []
    for sentence in tqdm(sentences):
        label = []
        for word in sentence:
            #TODO: Regex to check if the word is a bad word
            if word in bad_words_set:
                label.append(1)
            else:
                label.append(0)
        labels.append(label)
    return labels

bad_words = get_bad_words('data/bad-words.csv')
# Converting the list to a set
bad_words_set = set(bad_words)
# Importing dataset
dataset = pd.read_csv('data/comments_preprocessed.csv',header=0)
sentences,pos_tags_dataset = get_sentences_postags(dataset)


