import os
import re

#Save triples for each relation in a text file.
def print_triples(path, specialization,time,size,similarity,purpose):
    with open(path + 'specialization.txt', 'w') as f:
        for _list in specialization:
            for _string in _list:
                f.write(str(_string[0]) + '\t' + 'specialization' + '\t' + str(_string[2]) + '\n')

    with open(path + 'time.txt', 'w') as f:
        for _list in time:
            for _string in _list:
                f.write(str(_string[0]) + '\t' + 'time' + '\t' + str(_string[2]) + '\n')

    with open(path +'size.txt', 'w') as f:
        for _list in size:
            for _string in _list:
                f.write(str(_string[0]) + '\t' + 'size' + '\t' + str(_string[2]) + '\n')

    with open(path + 'similarity.txt', 'w') as f:
        for _list in similarity:
            for _string in _list:
                f.write(str(_string[0]) + '\t' + 'similarity' + '\t' + str(_string[2]) + '\n')

    with open(path + 'purpose.txt', 'w') as f:
        for _list in purpose:
            for _string in _list:
                f.write(str(_string[0]) + '\t' + 'purpose' + '\t' + str(_string[2]) + '\n')

    #And then, merge them in a unique file.
    filenames = [path + 'specialization.txt', path + 'time.txt', path +'size.txt', path + 'similarity.txt', path + 'purpose.txt']
    with open(path + 'triples.tsv', 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

    #Remove the useless files.
    for f in filenames:
        os.remove(f)

    return None

#Save examples for each relation in a text file
def print_examples(path,spec_example,time_example,size_example,simi_example,purp_example):
    with open(path + 'spec_example.txt', 'w') as f:
        for _list in spec_example:
            for _string in _list:
                f.write(str(_string) + '\n')

    with open(path + 'time_example.txt', 'w') as f:
        for _list in time_example:
            for _string in _list:
                f.write(str(_string) + '\n')

    with open(path +'size_example.txt', 'w') as f:
        for _list in size_example:
            for _string in _list:
                f.write(str(_string) + '\n')

    with open(path + 'similarity_example.txt', 'w') as f:
        for _list in simi_example:
            for _string in _list:
                f.write(str(_string) + '\n')

    with open(path + 'purpose_example.txt', 'w') as f:
        for _list in purp_example:
            for _string in _list:
                f.write(str(_string) + '\n')

    # And then, merge them in a unique file.
    filenames = [path + 'spec_example.txt', path + 'time_example.txt', path +'size_example.txt', path + 'similarity_example.txt', path + 'purpose_example.txt']
    with open(path + 'examples.txt', 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

    # Remove the useless files.
    for f in filenames:
        os.remove(f)

    return None

#Generate Question-Answer pairs
def q_a_pairs(path,spec_example, time_example, size_example, simi_example, purp_example):
    print_examples(path, spec_example, time_example, size_example, simi_example, purp_example)

    #Take triples
    triple=[trp for line in open(path + 'triples.tsv', 'r') for trp in line.split('\n')]
    triples=[t for trp in triple for t in trp.split('\t')]
    for i,t in enumerate(triples):
        if t=='':
            triples.pop(i)

    #Take sentences
    examples=[sentence for line in open(path + 'examples.txt', 'r') for sentence in line.split('\n')]
    del examples[1::2]
    seen = set()
    ex = []
    for item in examples:
        if item not in seen:
            seen.add(item)
            ex.append(item)

    #Take Patterns
    pt=open(path + 'patterns.tsv', 'r')
    pattern = pt.read()
    patterns=re.findall('(.*?)\t',pattern)

    #Initialize booleans to change the question
    spec=False
    spec1=False
    tim=False
    tim1=False
    siz=False
    siz1=False
    simi=False
    simi1=False
    purp=False
    purp1=False

    #Write Q-A
    with open(path + 'question-answer_pairs.txt', 'w') as outfile:
        for i in range(1,len(triples),3):
            if triples[i]=='specialization' and spec==False and spec1==False:
                outfile.write(patterns[0].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1])+'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                spec=True

            elif triples[i]=='specialization' and spec==True and spec1==False:
                outfile.write(patterns[1].replace('X',str(triples[i-1])).replace('Y',str(triples[i+1])) + '\t' + 'Yes' +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                spec1=True

            elif triples[i]=='specialization' and spec==True and spec1==True:
                outfile.write(patterns[2].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1])+'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                spec=False
                spec1=False

            if triples[i]=='time' and tim==False and tim1==False:
                outfile.write(patterns[13].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                tim=True

            elif triples[i]=='time' and tim==True and tim1==False:
                outfile.write(patterns[14].replace('X',str(triples[i-1])).replace('Y', str(triples[i+1])) + '\t' + 'Yes' +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                tim1=True

            elif triples[i]=='time' and tim==True and tim1==True:
                outfile.write(patterns[12].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                tim=False
                tim1=False

            if triples[i]=='size' and siz==False and siz1==False:
                outfile.write(patterns[6].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                siz=True

            elif triples[i]=='size' and siz==True and siz1==False:
                outfile.write(patterns[7].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                siz1=True

            elif triples[i]=='size' and siz==True and siz1==True:
                outfile.write(patterns[8].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                siz = False
                siz1 = False

            if triples[i]=='similarity' and simi==False and simi1==False:
                outfile.write(patterns[3].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                simi=True

            elif triples[i]=='similarity' and simi==True and simi1==False:
                outfile.write(patterns[4].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                simi1=True

            elif triples[i]=='similarity' and simi==True and simi1==True:
                outfile.write(patterns[5].replace('X',str(triples[i-1])).replace('Y',str(triples[i+1])) + '\t' + 'Yes' +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                simi=False
                simi1=False

            if triples[i]=='purpose' and purp==False and purp1==False:
                outfile.write(patterns[9].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                purp = True

            elif triples[i]=='purpose' and purp==True and purp1==False:
                outfile.write(patterns[10].replace('X',str(triples[i-1])) + '\t' + str(triples[i+1]) +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                purp1=True

            elif triples[i]=='purpose' and purp==True and purp1==True:
                outfile.write(patterns[11].replace('X',str(triples[i-1])).replace('Y',str(triples[i+1])) + '\t' + 'Yes' +'\t'+ str(triples[i]) +'\t'+ str(ex[0]) + '\t' + str(triples[i-1]) + '\t' + str(triples[i+1]) + '\n')
                ex.pop(0)
                purp = False
                purp1 = False

        # Remove the useless file
        os.remove(path + 'examples.txt')

        return None