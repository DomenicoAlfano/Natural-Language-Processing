from keras.layers import Activation, Dense, Embedding, Bidirectional, Dropout
from keras.layers.recurrent import LSTM
from keras.optimizers import RMSprop
from keras.models import Sequential
from keras import metrics
from util import *
import numpy as np
import pickle
import spacy
import json
import os
import re

kdb_path = '/Users/domenicoalfano/PycharmProjects/Bot/files/kdbtext/'

# special vocabulary symbols
_PAD = "_PAD"
_UNK = "_UNK"
yes_or_not = "yes_or_not"
classic = "classic"

PAD_ID = 0
UNK_ID = 1

_yes_or_not_id = 2
_classic_id = 3

#limit
question_limit = 20

# load spacy
nlp = spacy.load('en_default')

# filter data
def get_data(data):
    questions, answers = [], []
    counter = 0
    for item in data:
        question = nlp.tokenizer(item['question'].lower())
        if len(question) <= question_limit:
            answer = nlp.tokenizer(item['answer'].lower())
            questions.append(question)
            answers.append(answer)
    return questions, answers

def create_vocabulary(data):
    vocab = {}
    for line in data:
        for word in line:
            if word.orth_ in vocab:
                vocab[word.orth_] += 1
            else:
                vocab[word.orth_] = 1

    vocab_list = sorted(vocab, key=vocab.get, reverse=True)

    print('Create vocabulary')
    vocab_set = set(vocab_list)
    embeddings = {_PAD: np.zeros(300), _UNK: np.ones(300), yes_or_not: np.zeros(300), classic: np.ones(300)}
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

# prepare data
def build_data(data, data_voc, target_voc, target):
    if target != None:
        x = []
        y = np.zeros((len(target), len(target_voc)))
        for q, question in enumerate(data):
            x.append([data_voc.get(word.orth_, UNK_ID) for word in question] + [PAD_ID] * (question_limit - len(question)))

        for a, answer in enumerate(target):
            if str(answer) != 'yes' and str(answer) != 'y' and str(answer) != 'no' and str(answer) != 'yes!':
                y[a, target_voc[classic]] = 1
            else:
                y[a,target_voc[yes_or_not]] = 1

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

def get_context(query, data_voc, target_voc, model):
    query_tok = nlp.tokenizer(query.lower())
    nlp.tagger(query_tok)
    nlp.parser(query_tok)
    X_pred = build_data(query_tok, data_voc, target_voc, None)
    y_pred = get_predict(X_pred, model)
    ctx=list(target_voc)[y_pred]
    return ctx

def collect_data(kdb_path):
    print('Start!')
    questions=[]
    answers=[]
    for f in path_file(kdb_path):
        file_object = open(f, 'r')
        text = json.loads(file_object.read())
        q, a = get_data(text)
        questions = questions + q
        answers = answers + a

    print('Collecting..')
    data_voc, embedding_matrix = create_vocabulary(questions)
    target_voc = {_PAD: PAD_ID, _UNK: UNK_ID, yes_or_not: _yes_or_not_id, classic: _classic_id}
    X_train, y_train = build_data(questions, data_voc, target_voc, answers)

    #save vocabularies
    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/context/data_voc', 'wb') as output:
        pickle.dump(data_voc, output, pickle.HIGHEST_PROTOCOL)
    with open('/Users/domenicoalfano/PycharmProjects/Bot/files/context/target_voc', 'wb') as output:
        pickle.dump(target_voc, output, pickle.HIGHEST_PROTOCOL)

    return X_train, y_train, embedding_matrix, data_voc, target_voc

# Training
def train(kdb_path):
    X_train, y_train, embedding_matrix, data_voc, target_voc = collect_data(kdb_path)
    print('Build model...')
    model = Sequential()
    model.add(Embedding(len(data_voc), 300, input_length = question_limit, trainable = False, mask_zero = True, weights = [embedding_matrix]))
    model.add(Bidirectional(LSTM(128)))
    model.add(Dropout(0.5))
    model.add(Dense(len(target_voc)))
    model.add(Activation('softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = [metrics.categorical_accuracy])
    model.fit([X_train], [y_train], batch_size = 64, epochs = 1)
    model.save('/Users/domenicoalfano/PycharmProjects/Bot/files/Context_Classifier/model.keras')

    return None

# Run this code line to train the context classifier
# train(kdb_path)