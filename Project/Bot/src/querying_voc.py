from util import *
import numpy as np
import pickle
import spacy
import json
import os
import re

kdb_path = '/Users/domenicoalfano/PycharmProjects/Bot/files/kdbtext/'

# load spacy
nlp = spacy.load('en_default')

#filter data
def get_data_yes_or_not(data):
    questions = []
    counter = 0
    for item in data:
        question = nlp.tokenizer(item['question'].lower())
        answer = nlp.tokenizer(item['answer'].lower())
        if (str(answer)=='yes' or str(answer)=='no' or str(answer)=='yes!' or str(answer)=='y'):
            nlp.tagger(question)
            nlp.parser(question)
            questions.append(question)
    return questions

#filter data
def get_data_classic(data):
    questions = []
    counter = 0
    for item in data:
        question = nlp.tokenizer(item['question'].lower())
        answer = nlp.tokenizer(item['answer'].lower())
        if str(answer)!='yes' and str(answer)!='y' and str(answer)!='no'and str(answer)!='yes!':
            nlp.tagger(question)
            nlp.parser(question)
            questions.append(question)
    return questions

def collect_vocabulary(kdb_path):
    print('Collecting data')
    yes_or_not=[]
    classic=[]
    for f in path_file(kdb_path):
        file_object = open(f, 'r')
        text = json.loads(file_object.read())
        c = get_data_yes_or_not(text)
        d = get_data_classic(text)
        yes_or_not = yes_or_not + c
        classic = classic + d

    print('Create Vocabulary')
    data_voc_yes_or_not = create_new_voc(yes_or_not)
    data_voc_classic = create_new_voc(classic)

    #save vocs
    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_yes_or_not', 'wb') as output:
        pickle.dump(data_voc_yes_or_not, output, pickle.HIGHEST_PROTOCOL)

    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_classic', 'wb') as output:
        pickle.dump(data_voc_classic, output, pickle.HIGHEST_PROTOCOL)

    print('Saved')
    return None

# Run this code line to create the vocabs
# collect_vocabulary(kdb_path)