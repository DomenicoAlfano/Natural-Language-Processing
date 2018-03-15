from keras.layers import Activation, Dense, Embedding, Bidirectional, Dropout
from keras.layers.recurrent import LSTM
from keras.optimizers import RMSprop
from keras.models import Sequential
from keras import metrics
import numpy as np
from util import *
import pickle
import spacy
import json
import os
import re

kdb_path = '/Users/domenicoalfano/PycharmProjects/Bot/files/kdbtext/'

# special vocabulary symbols
_PAD = '_PAD'
_UNK = '_UNK'

PAD_ID = 0
UNK_ID = 1

#limit
question_limit = 20

# load spacy
nlp = spacy.load('en_default')

# filter data
def get_data(data):
    questions, relations = [], []
    counter = 0
    for item in data:
        question = nlp.tokenizer(item['question'].lower())
        if len(question) <= question_limit:
            nlp.tagger(question)
            nlp.parser(question)
            relation = item['relation']
            questions.append(question)
            relations.append(relation)
    return questions, relations

def create_vocabulary(data, label=False):
    if not label:
        vocab = {}
        for line in data:
            for word in line:
                if word.orth_ in vocab:
                    vocab[word.orth_] += 1
                else:
                    vocab[word.orth_] = 1

        vocab_list = sorted(vocab, key=vocab.get, reverse=True)

        print('Getting embeddings')
        vocab_set = set(vocab_list)
        embeddings = {_PAD: np.zeros(300), _UNK: np.ones(300)}
        with open('/Users/domenicoalfano/PycharmProjects/Bot/files/glove.840B.300d.txt', 'r') as glove_file:
            for line in glove_file:
                try:
                    tokens = line.split()
                    word = tokens[0].lower()
                    if word in vocab_set:
                        embeddings[word] = np.asarray(tokens[1:], dtype=np.float32)
                except ValueError:
                    pass
            return dict([(x, y) for (y, x) in enumerate(embeddings)]), np.asarray(list(embeddings.values()))
    return dict([(x, y) for (y, x) in enumerate(set(data))])

# prepare data
def build_data(data, data_voc, target_voc, target):
    if target != None:
        x = []
        y = np.zeros((len(target), len(target_voc))) if target else np.array(())
        for q, question in enumerate(data):
            x.append([data_voc.get(word.orth_, UNK_ID) for word in question] + [PAD_ID] * (question_limit - len(question)))
            y[q, target_voc[target[q]]] = 1
        return np.array(x), y
    else:
        x = []
        x.append([data_voc.get(word.orth_, UNK_ID) for word in data] + [PAD_ID] * (question_limit - len(data)))
        return np.array(x)

# get prediction
def get_predict(x, model):
    dev = np.array(x)
    pred = model.predict([dev])
    return np.argmax(pred[0])

def get_relation(query, data_voc, target_voc, model):
    query_tok = nlp.tokenizer(query.lower())
    nlp.tagger(query_tok)
    nlp.parser(query_tok)
    X_pred = build_data(query_tok, data_voc, target_voc, None)
    y_pred = get_predict(X_pred, model)
    rel=list(target_voc)[y_pred]
    return rel

def collect_data(kdb_path):
    print('Start!')
    questions=[]
    relations=[]
    for f in path_file(kdb_path):
        file_object = open(f, 'r')
        text = json.loads(file_object.read())
        q, r = get_data(text)
        questions = questions + q
        relations = relations + r

    print('Collecting..')
    data_voc, embedding_matrix = create_vocabulary(questions)
    target_voc = create_vocabulary(relations, label=True)
    X_train, y_train = build_data(questions, data_voc, target_voc, relations)

        #save vocabularies
    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/data_voc', 'wb') as output:
        pickle.dump(data_voc, output, pickle.HIGHEST_PROTOCOL)
    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/target_voc', 'wb') as output:
        pickle.dump(target_voc, output, pickle.HIGHEST_PROTOCOL)

    return X_train, y_train, embedding_matrix, data_voc, target_voc

def train(kdb_path):
    X_train, y_train, embedding_matrix, data_voc, target_voc = collect_data(kdb_path)
    print('Building model')
    model = Sequential()
    model.add(Embedding(len(data_voc), 300, input_length = question_limit, trainable = False, mask_zero = True, weights = [embedding_matrix]))
    model.add(Bidirectional(LSTM(128)))
    model.add(Dropout(0.5))
    model.add(Dense(len(target_voc)))
    model.add(Activation('softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = [metrics.categorical_accuracy])
    model.fit([X_train], [y_train], batch_size = 64, epochs = 1)
    model.save('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/model.keras')

    return None

# Uncomment this code line to train the relation classifier
# train(kdb_path)