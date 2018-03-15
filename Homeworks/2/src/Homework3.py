import re
import os
import gzip
import spacy
import networkx as nx
import xml.etree.ElementTree as ET

#Initialize Spacy
nlp = spacy.load('en')

#Take the path of all the file
def path_file(path):
    list_f=[]
    for subdir, dirs, files in os.walk(path):
        for file in files:
            list_f.append(str(os.path.join(subdir, file)))

    for i, j in enumerate(list_f):
        if '.DS_Store' in j:
            list_f.pop(i)

    return list_f

#Navigate into xml to extract information
def parse_xml(texts,root):
    # Clean Text. As specified in DEFIE, this method works better with simple sentence.
    clean_text = []
    for sentence in texts:
        sent=(re.sub("[\(\[].*?[\)\]]", "", str(sentence)))
        clean_text.append(" ".join(sent.split()))

    #Collect mentions
    mentions_index={(i[1].text, int(i[2].text)) for i in root[1]}
    mentions_index=sorted(mentions_index, key=lambda mentions_index:mentions_index[1])

    #Extract disambiguated words
    word_in=[[]]
    index_m =0

    for s,sentence in enumerate(texts):
        index_word = 0
        for m, mention in enumerate(mentions_index[index_m:]):
            found = 0
            for w,word in enumerate(sentence.split()[index_word:]):
                if word==mention[0].split()[0]:
                    word_in[-1].append(mention[0])
                    index_word += w
                    found = 1
                    break
            if not found:
                index_m += m
                word_in.append([])
                break

    return clean_text, word_in

#Disambiguate sentences
def disambiguate_sentences(clean_text, word_in):
    sents=[]
    for s, sentence in enumerate(clean_text):
        sents.append(nlp(sentence))
        try:
            for word in word_in[s]:
                start=sentence.find(word)
                sents[-1].merge(start, start+len(word))
        except IndexError:
            return None
    return sents

#Build Semantic Graph
def get_edges(semantic_graph):
    edges = []
    for token in semantic_graph:
        for child in token.children:
            edges.append((token, child))
    return edges

#Extract triples from the sentences
def give_triples(sentence):
    #Build nx graph
    graph = (nx.Graph(get_edges(sentence)))
    #Extract dirty paths
    all_paths = nx.all_pairs_shortest_path(graph).values()
    dirty_paths = [nd for node_paths in all_paths for nd in node_paths.values()]

    #Clean "dirty" paths, taking paths that connect Subject-Verb-Object and Subject-Verb-Adjective nodes
    subject = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
    object = ["dobj", "oprd", "attr", "iobj", "pobj","dative"]

    clean_paths = []

    for path in dirty_paths:
        for i in range(len(path)):
            for sub in subject:
                for ob in object:
                    if path[0].dep_ != sub or path[i].pos_ != 'VERB' or path[-1].dep_ != ob:
                        continue
                    clean_paths.append(path)

    # Build Triples from clean paths
    triple=[]
    for path in clean_paths:
        trp = list()
        trp.append(str(path[0]))
        trp.append(' '.join(map(str, path[1:-1])))
        trp.append(str(path[-1]))
        triple.append(trp)

    #Clean triples
    words = ['This', 'That', 'Those', 'These', 'He', 'She', 'Him', 'Her', 'There', 'One', 'this', 'that','he','she','him','they','They','what',
             'her','those', 'these', 'there', 'one', 'who', 'Who', 'it', 'It', 'which', 'Which','By','by','when', 'When', ',' ,'%','What','part']

    for i,trp in enumerate(triple):
        for w in words:
            if w==trp[0]:
                triple.pop(i)

    for i,trp in enumerate(triple):
        for w in words:
            if w==trp[-1]:
                triple.pop(i)

    return triple

################################################_RELATIONS_################################################

####_SPECIALIZATION_####
def spec_rel(triples,disam_sents):
    spec_pattern='is'
    specialization=[]
    counter=[]

    for i, triple in enumerate(triples):
        for trp in triple:
            if trp[0].islower() == False and trp[0].isdigit() == False and len(trp[0])!=1:
                if spec_pattern == trp[1] and len(trp[1].split()) == 1:
                    specialization.append(trp)
                    counter.append(i)

    #Delete triples that cointaining information for size relation.
    spec_pattern2 = ['large','big','small','tall','huge','massive','microscopip','narrow','short','old','new']

    for i,t in enumerate(specialization):
        for pattern in spec_pattern2:
             if pattern in t[-1]:
                 if specialization:
                    specialization.pop(i)
                    counter.pop(i)

    #Delete duplicates
    b_set = set(tuple(x) for x in specialization)
    b = [ list(x) for x in b_set ]

    #Take the sentences associated with the triples
    true_sents=[]
    for j in range(len(counter)):
        true_sents.append(disam_sents[counter[j]])

    return b, true_sents

####_TIME_####
def time_rel(triples,disam_sents):
    time_pattern='created in'
    time=[]
    counter=[]

    for i, triple in enumerate(triples):
        for trp in triple:
            if trp[1]==time_pattern and any(char.isdigit() for char in trp[-1])==True and trp[0].islower() == False:
                time.append(trp)
                counter.append(i)

    #Delete duplicates
    b_set = set(tuple(x) for x in time)
    b = [ list(x) for x in b_set ]

    #Take the sentences associated with the triples
    true_sents=[]
    for j in range(len(counter)):
        true_sents.append(disam_sents[counter[j]])

    return b, true_sents

####_SIZE_####
def size_rel(triples,disam_sents):
    size_pattern='is'
    size_pattern2=['big','large','small','tall','huge','massive','microscopip','narrow','short','little','slim','fat','gigantic','giant','mini']
    size=[]
    counter=[]

    for i, triple in enumerate(triples):
        for trp in triple:
            for pattern2 in size_pattern2:
                if trp[1]==size_pattern and trp[-1] == pattern2:
                    size.append(trp)
                    counter.append(i)

    #Delete duplicates
    b_set = set(tuple(x) for x in size)
    b = [ list(x) for x in b_set ]

    #Take the sentences associated with the triples
    true_sents=[]
    for j in range(len(counter)):
        true_sents.append(disam_sents[counter[j]])

    return b, true_sents

####_SIMILARITY_####
def similarity_rel(triples,disam_sents):
    similarity_pattern='confused with'
    similarity=[]
    counter=[]

    for i,triple in enumerate(triples):
        for trp in triple:
            if trp[1]==similarity_pattern:
                similarity.append(trp)
                counter.append(i)

    #Delete duplicates
    b_set = set(tuple(x) for x in similarity)
    b = [ list(x) for x in b_set ]

    #Take the sentences associated with the triples
    true_sents=[]
    for j in range(len(counter)):
        true_sents.append(disam_sents[counter[j]])

    return b, true_sents

####_PURPOSE_####
def purpose_rel(triples,disam_sents):
    purpose_pattern=['used as','used for']
    purpose=[]
    counter=[]

    for i,triple in enumerate(triples):
        for trp in triple:
            for pattern in purpose_pattern:
                if trp[1]==pattern and trp[0].islower() == False:
                    purpose.append(trp)
                    counter.append(i)

    #Delete duplicates
    b_set = set(tuple(x) for x in purpose)
    b = [ list(x) for x in b_set ]

    #Take the sentences associated with the triples
    true_sents=[]
    for j in range(len(counter)):
        true_sents.append(disam_sents[counter[j]])

    return b, true_sents