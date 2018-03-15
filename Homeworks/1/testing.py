from NLP2 import Morph
import sklearn_crfsuite as crf
import numpy as np
import matplotlib.pyplot as plt
import re
import pickle

train_file_eng = 'task1_data/training.eng.txt'
test_file_eng = 'task1_data/test.eng.txt'
dev_file_eng = 'task1_data/dev.eng.txt'

train_file_ita = 'task2_data/train.it.txt'
test_file_ita = 'task2_data/test.it.txt'
dev_file_ita = 'task2_data/dev.it.txt'

train_extra ='extra_task_data/training.eng.txt'

def print_score_f1(crfsuite, model,prediction,labels):
    crfsuite.score(model.testing_label, prediction)
    return crf.metrics.flat_f1_score(model.testing_label, prediction, average='weighted', labels=labels)


def print_tag_score(crfsuite, model, prediction,labels):
    crfsuite.score(model.testing_label, prediction)
    sorted_labels = sorted(labels, key=lambda name: (name[1:], name[0]))
    return crf.metrics.flat_classification_report(model.testing_label, prediction, labels=sorted_labels, digits=4)



def optimize_delta(max,train,test, save_model):
    score = []
    for i in range(max+1):
        print('Runnig model for delta:'+str(i))
        model = Morph(i, train, test)
        c = crf.CRF(algorithm='ap', max_iterations=100)
        c.fit(model.training_feature,model.training_label)
        labels = list(c.classes_)
        labels.remove('START')
        labels.remove('STOP')
        prediction = c.predict((model.testing_feature))
        f1=print_score_f1(c, model,prediction,labels)
        precision = crf.metrics.flat_precision_score(model.testing_label,prediction, average='weighted', labels=labels)
        tag_scores = print_tag_score(c, model,prediction,labels)
        rec = re.compile(r'avg \/ total(.*)', flags=re.DOTALL)
        recall = rec.findall(tag_scores)[0]
        recall = recall.split()[1]
        print('F1_Score:'+str(f1))
        print('Precision:'+str(precision))
        print('Recall: '+str(recall))
        print('Tag Score: \n'+tag_scores)

        score.append([i, f1, precision,recall])
        if save_model == i :
            pickle.dump(c, open("crf_model.model", "wb"))
    return np.asarray(score)


score = optimize_delta(8,train_file_eng,dev_file_eng,5)
ind = np.arange(len(score))
fig, ax = plt.subplots(figsize=(8,4))
ax.grid(axis='y')
plt.title('Scores')
ax.plot(ind, score[:,1], c='green', label='F1',linewidth=0.5)
ax.plot(ind, score[:,2], c='red',label='Precision',linewidth=0.5)
ax.plot(ind, score[:,3], c='blue',label='Recall',linewidth=0.5)
ax.legend(loc='lower right')
plt.savefig('plot_result.png',format='png', dpi=200)
plt.show()


# pickle.dump(c, open("crf_model.model", "wb"))
# pickle.dump(c, open("ita_model.model", "wb"))
# pickle.dump(c, open("extra_model.model", "wb"))
