import requests
import spacy
import ujson
import os

nlp = spacy.load('en_default')

key = '15a969f5-69bf-4440-a95e-f12aeed558d3'

def path_file(kdb_path):
    list_f=[]
    for subdir, dirs, files in os.walk(kdb_path):
        for file in files:
            list_f.append(str(os.path.join(subdir, file)))

    for i, j in enumerate(list_f):
        if '.DS_Store' in j:
            list_f.pop(i)

    return list_f

def get_dict(file):
    with open(file) as f:
        rows = (line.split('\t') for line in f)
        dict = {row[0]: row[1:] for row in rows}
    return dict

def domains_button(dict):
    buttons=[]
    for i in range(len(dict.keys())):
        buttons.append([list(dict.keys())[i]])
    return buttons

def get_obj(answer):
    obje = ['dobj', 'oprd', 'iobj', 'pobj']
    attr = ['attr','dative','acomp','appos']
    ans=nlp(answer)
    find = []
    for word in ans:
        if word.dep_ in attr:
            find.append(word)
    if find:
        return str(find[-1])
    else:
        for word in ans:
            if word.dep_ in obje:
                return str(word)

def get_infomation(query, label=False):
    if not label:
        subjects = ['nsubj', 'nsubjpass', 'csubj', 'csubjpass', 'agent', 'expl']
        objects = ['dobj', 'oprd', 'iobj', 'pobj', 'attr','dative','appos']
        q=nlp(query.lower())
        for word in q:
            if word.dep_ in subjects:
                sub = word

        for word in q:
            if word.dep_ in objects:
                ob = word

        return str(sub), str(ob)

    subjects = ['nsubj', 'nsubjpass', 'csubj', 'csubjpass', 'agent', 'expl']
    s = ['dobj', 'oprd', 'iobj', 'pobj', 'attr','dative','appos']
    q = nlp(query.lower())
    store = []
    for word in q:
        if word.dep_ in subjects:
            store.append(str(word))

    if store:
        return store[-1]

    else:
        for word in q:
            if word.dep_ in s:
                store.append(str(word))
        return store[-1]

def disambiguate(word):
    babelfy_url = "https://babelfy.io/v1/disambiguate?"
    params = "text=" + word + "&lang=EN&key=" + key
    get_res = requests.get(babelfy_url, params = params)
    response = get_res.text
    if get_res.status_code ==200:
        decoded = ujson.decode(response)
        if u'message' in decoded:
            raise StopIteration(decoded['message'])
    else:
        raise Exception(get_res.text)

    dictionary = ujson.decode(response)[0] if ujson.decode(response) else None

    return dictionary['babelSynsetID'] if dictionary else None

def create_new_voc(data):
    vocab = {}
    for line in data:
        for word in line:
            if word.orth_ in vocab:
                vocab[word.orth_] += 1
            else:
                vocab[word.orth_] = 1

    vocab_list = sorted(vocab, key=vocab.get, reverse=True)
    vocab_set = set(vocab_list)
    return dict([(x, y) for (y, x) in enumerate(vocab_set)])