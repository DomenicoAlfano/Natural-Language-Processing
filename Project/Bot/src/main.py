from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from nltk.tokenize import word_tokenize
from telepot.loop import MessageLoop
from keras.models import load_model
import relation_classifier
import context_classifier
import pprint as pp
from util import *
from kbs import *
import telepot
import pickle
import random
import time

TOKEN = '432078963:AAH3BLtr7JxgHL-RcsdHYZzWpjB1wMsITr0'
bot = telepot.Bot(TOKEN)

domains_file = '/Users/domenicoalfano/PycharmProjects/Bot/files/domains_to_relations.tsv'
subj_file = '/Users/domenicoalfano/PycharmProjects/Bot/files/domain_subj.txt'
kdb_path = '/Users/domenicoalfano/PycharmProjects/Bot/files/kdbtext/'

state = 0

dict = get_dict(domains_file)
domain_to_subj = get_dict(subj_file)

def handle(msg):
    global state
    global domain
    global queryst
    global found
    global data
    global relation
    global subject
    global object
    global data_voc

    dom = domains_button(dict)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    pp.pprint(msg)

    if state == 0 and msg['text']=='/start':
        state = 1
        kb_markup = ReplyKeyboardMarkup(keyboard=dom, one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id, text='What do you want to talk about?', reply_markup=kb_markup)

    if state == 1 and msg['text'] in dict.keys():
        domain = msg['text']
        state = 2
        kb_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Querying")], [KeyboardButton(text="Enriching")]], one_time_keyboard=True)
        bot.sendMessage(chat_id, text='Please, select the direction of interaction.', reply_markup=kb_markup)

    if state == 2 and msg['text'] == 'Querying':
        state = 3
        bot.sendMessage(chat_id, text='Ok, send me a question!')

    if state == 3 and '?' in msg['text']:
        queryst=msg['text']

        #Get relation
        rel_classifier = load_model('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/model.keras')
        data_voc_rel = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/data_voc', 'rb'))
        target_voc_rel = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Relation_Classifier/target_voc', 'rb'))
        relation = relation_classifier.get_relation(msg['text'], data_voc_rel, target_voc_rel, rel_classifier)

        #Take the type of the question
        context_model = load_model('/Users/domenicoalfano/PycharmProjects/Bot/files/Context_Classifier/model.keras')
        data_voc_context = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Context_Classifier/data_voc', 'rb'))
        target_voc_context = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Context_Classifier/target_voc', 'rb'))
        ctx = context_classifier.get_context(msg['text'], data_voc_context, target_voc_context, context_model)
        bot.sendMessage(chat_id, text=ctx)
        bot.sendMessage(chat_id, text='The relation of the question is: ' + relation)

        if ctx == 'yes_or_not':
            subject, object = get_infomation(msg['text'])
            data_voc = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_yes_or_not', 'rb'))
            found = False
            if (subject in data_voc) and (object in data_voc):
                for f in path_file(kdb_path):
                    file_object = open(f, 'r')
                    text = json.loads(file_object.read())
                    for item in text:
                        if subject in word_tokenize(item['question'].lower()) and object in word_tokenize(item['question'].lower()) and item['relation'] == relation \
                            and (item['answer'] == 'yes' or item['answer'] == 'y' or item['answer'] == 'no' or item['answer'] == 'No'\
                            or item['answer'] == 'Yes' or item['answer'] == 'Yes!' or item['answer'] == 'No!'):
                            found = True
                            bot.sendMessage(chat_id, text=item['answer'])
                            state = 0
                            bot.sendMessage(chat_id, text='Digit /start to restart the conversation.')
                            break
                    if found:
                        break

            if found == False:
                bot.sendMessage(chat_id, text='I don\'t know it but if you know the answer, please, write it to me. If you don\'t know the answer digit /restart')
                state = 4

        else:
            subject = get_infomation(msg['text'], label=True)
            data_voc = pickle.load(open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_classic', 'rb'))
            found = False
            if subject in data_voc:
                for f in path_file(kdb_path):
                    file_object = open(f, 'r')
                    text = json.loads(file_object.read())
                    for item in text:
                        if subject in word_tokenize(item['question'].lower()) and item['relation'] == relation and item['answer'] != 'yes' \
                            and item['answer'] != 'y' and item['answer'] != 'no' and item['answer'] != 'No' \
                            and item['answer'] != 'Yes' and item['answer'] != 'Yes!' and item['answer'] != 'No!':
                            if subject == get_infomation(item['question'].lower(), label=True):
                                found = True
                                bot.sendMessage(chat_id, text=item['answer'])
                                state = 0
                                bot.sendMessage(chat_id, text='Digit /start to restart the conversation.')
                                print(f)
                                break
                        if found:
                            break
                    if found:
                        break

            if found == False:
                bot.sendMessage(chat_id,text='I don\'t know it but if you know the answer, please, write it to me. If you don\'t know the answer digit /restart')
                state = 6

    if state == 4 and msg['text'] != '/restart' and msg['text'] != queryst:
        # UPDATE KBS
        user_ans=msg['text']
        data = {}
        data['question'] = queryst
        data['answer'] = user_ans
        data['relation'] = relation
        data['context'] = ' '
        data['domains'] = domain
        data['c1'] = subject+'::'+disambiguate(subject) if subject and disambiguate(subject) else subject if subject and not disambiguate(subject) else ' '
        data['c2'] = object+'::'+disambiguate(object) if object and disambiguate(object) else object if object and not disambiguate(object) else ' '
        add_item(data)

        # UPDATE and save vocabulary
        new_voc = create_new_voc([nlp(queryst)])
        data_voc.update(new_voc)
        with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_yes_or_not', 'wb') as output:
            pickle.dump(data_voc, output, pickle.HIGHEST_PROTOCOL)

        # UPDATE local KB
        items_from(x=get_my_last_id(kdb_path))

        bot.sendMessage(chat_id, text='Thank you! Digit /start to restart the conversation.')
        state=0

    if state == 4 and msg['text'] == '/restart':
        bot.sendMessage(chat_id, text='Digit /start to restart the conversation.')
        state = 0

    if state == 6 and msg['text'] != '/restart' and msg['text'] != queryst:
        #UPDATE KBS
        user_ans = msg['text']
        object = get_obj(user_ans)
        data = {}
        data['question'] = queryst
        data['answer'] = user_ans
        data['relation'] = relation
        data['context'] = ' '
        data['domains'] = domain
        data['c1'] = subject+'::'+disambiguate(subject) if subject and disambiguate(subject) else subject if subject and not disambiguate(subject) else ' '
        data['c2'] = object+'::'+disambiguate(object) if object and disambiguate(object) else object if object and not disambiguate(object) else ' '
        add_item(data)

        # UPDATE and save vocabulary
        new_voc = create_new_voc([nlp(queryst)])
        data_voc.update(new_voc)
        with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/data_voc_classic', 'wb') as output:
            pickle.dump(data_voc, output, pickle.HIGHEST_PROTOCOL)

        # UPDATE local KB
        items_from(x=get_my_last_id(kdb_path))

        bot.sendMessage(chat_id, text='Thank you! Digit /start to restart the conversation.')
        state = 0

    if state == 6 and msg['text'] == '/restart':
        bot.sendMessage(chat_id, text='Digit /start to restart the conversation.')
        state = 0

    if state == 2 and msg['text'] == 'Enriching':
        relations = []
        for i,j in enumerate(dict[domain]):
            relations.append([j])

        relation=random.choice(relations)[0]

        subjects = []
        for i,j in enumerate(domain_to_subj[domain]):
            subjects.append([j])

        subject = random.choice(subjects)[0] if random.choice(subjects)[0] else random.choice(subjects)[0]

        bot.sendMessage(chat_id, text='The relation selected is: ' + relation)
        patterns = open('/Users/domenicoalfano/PycharmProjects/Bot/files/patterns/'+relation.strip()+'.txt','r')
        queryst = random.choice(patterns.read().split('\n')).replace('$X$',subject)
        bot.sendMessage(chat_id, text=queryst)

        state = 10

    if state == 10 and msg['text'] != 'Enriching':
        # UPDATE KBS
        user_answer = msg['text']
        object = get_obj(user_answer) if len(user_answer)>1 else user_answer
        data = {}
        data['question'] = queryst
        data['answer'] = user_answer
        data['relation'] = relation.upper()
        data['context'] = ' '
        data['domains'] = domain
        data['c1'] = subject+'::'+disambiguate(subject) if subject and disambiguate(subject) else subject if subject and not disambiguate(subject) else ' '
        data['c2'] = object+'::'+disambiguate(object) if object and disambiguate(object) else object if object and not disambiguate(object) else ' '
        add_item(data)

        # UPDATE vocabulary
        new_voc = create_new_voc([nlp(queryst)])
        data_voc.update(new_voc)
        with open('/Users/domenicoalfano/PycharmProjects/Bot/files/Querying/classic/data_voc', 'wb') as output:
            pickle.dump(data_voc, output, pickle.HIGHEST_PROTOCOL)

        # UPDATE local KB
        items_from(x=get_my_last_id(kdb_path))

        bot.sendMessage(chat_id, text='Thank you! Digit /start to restart the conversation.')
        state = 0

MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(100)