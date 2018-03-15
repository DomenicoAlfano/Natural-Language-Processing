from Homework3 import *
from output import *

#Take a list of all the paths of the wikipedia files
# wiki_path='/Users/domenicoalfano/Master/NLP/Homework/3/hw3/babelfied-wikipediaXML/'
# list_file=path_file(wiki_path)

#The code below take in input the all the paths of the wikipedia files in a text file to speed up the process.
path_='/Users/domenicoalfano/Master/NLP/Homework/3/hw3/'
list_file = [line.rstrip('\n') for line in open(path_+'path.txt')]
for i,j in enumerate(list_file):
    if '.DS_Store' in j:
        list_file.pop(i)

#Inizialize list to save the triples and the sentences associated
specialization=[]
spec_example=[]
time=[]
time_example=[]
size=[]
size_example=[]
similarity=[]
simi_example=[]
purpose=[]
purp_example=[]

#Inizialize booleans to exit from the loop
comp_a = False
comp_b = False
comp_c = False
comp_d = False
comp_e = False

#For each wiki file
for f in list_file:
    #Open File
    file=gzip.open(f)
    found=False
    try:
        #Parse the file
        tree = ET.parse(file)
    #Some file introduce problems, probably because there are unrecognized character.
    except ET.ParseError:
        found=True
    if found==False:
        root = tree.getroot()
        #Take the text
        article=root[0].text
        #Some files are empty, so I need to put this condition
        if article is not None:
            #From text take the sentences
            sentences=article.split('\n')
            #Take only the clean sentences. As specified in DEFIE, this method works better with simple sentence.
            for i,s in enumerate(sentences):
                if '``' in s:
                    sentences.pop(i)
            #From the file take the words to disambiguate
            text, disam_word = parse_xml(sentences,root)

            #Disambiguate words
            disam_sents=disambiguate_sentences(text, disam_word)
            #I would be sure that the words are merged
            if disam_sents is not None:
                #Take all triples in the Article
                triples=[]
                for s in disam_sents:
                    triples.append(give_triples(s))

                # Take at least a specific number of triples for each relation and save the correspondent sentence
                if comp_a==False:
                    a,true_sent_a=spec_rel(triples,disam_sents)
                    if a and len(a)==1 and len(true_sent_a)==1:
                        specialization.append(a)
                        spec_example.append(true_sent_a)
                        if len(specialization)==50:
                            comp_a=True
                            print('Specialization completato')

                if comp_b==False:
                    b,true_sent_b=time_rel(triples,disam_sents)
                    if b and len(b)==1 and len(true_sent_b)==1:
                        time.append(b)
                        time_example.append(true_sent_b)
                        if len(time)==50:
                            comp_b=True
                            print('Time completato')

                if comp_c==False:
                    c,true_sent_c=size_rel(triples,disam_sents)
                    if c and len(c)==1 and len(true_sent_c)==1:
                        size.append(c)
                        size_example.append(true_sent_c)
                        if len(size)==20:
                            comp_c=True
                            print('Size completato')

                if comp_d==False:
                    d, true_sent_d=similarity_rel(triples,disam_sents)
                    if d and len(d)==1 and len(true_sent_d)==1:
                        similarity.append(d)
                        simi_example.append(true_sent_d)
                        if len(similarity)==30:
                            comp_d=True
                            print('Similarity completato')

                if comp_e==False:
                    e, true_sent_e=purpose_rel(triples,disam_sents)
                    if e and len(e)==1 and len(true_sent_e)==1:
                        purpose.append(e)
                        purp_example.append(true_sent_e)
                        if len(purpose)==30:
                            comp_e=True
                            print('Purpose completato')

    #When the relations are completed, exit from the loop
    if comp_a==True and comp_b==True and comp_c==True and comp_d==True and comp_e==True:
        break

#Folder to save files
path = '/Users/domenicoalfano/Master/NLP/Homework/3/alfano_1752007_homework_3/data/'

#Save triples for each relation in a text file.
print_triples(path, specialization, time, size, similarity, purpose)

#Generate Question-Answer pairs.
q_a_pairs(path,spec_example, time_example, size_example, simi_example, purp_example)