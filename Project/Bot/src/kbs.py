from util import *
import requests
import json

kdb_url = 'http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/'
key = '15a969f5-69bf-4440-a95e-f12aeed558d3'
kdb_path = '/Users/domenicoalfano/PycharmProjects/Bot/files/kdbtext/'

def add_item(item):
    assert (item['question'])
    assert (item['answer'])
    assert (item['relation'])
    assert (item['context'])
    assert (item['domains'])
    assert (item['c1'])
    assert (item['c2'])

    headers = {"content-type": "application/json"}
    params = {"key": key}
    url = kdb_url + 'add_item'

    response = requests.post(url, params = params, headers = headers, data = ujson.dumps(item))

    return None

def items_number_from(start_id=0):
    count = 0
    url = kdb_url + 'items_number_from?id=' + str(start_id) + '&key=' + key
    response = requests.get(url)
    count = count + int(response.text)
    return count

def get_my_last_id(kdb_path):
    my_last_id = 0
    for f in path_file(kdb_path):
        file_object = open(f, 'r')
        text = json.loads(file_object.read())
        for item in text:
            my_last_id += 1
    return my_last_id

def items_from(x = get_my_last_id(kdb_path)):
    while x <= items_number_from(start_id=0):
        url = kdb_url + 'items_from?id=' + str(x) + '&key=' + key
        response = requests.get(url)
        if response.text:
            db_file = open(kdb_path + 'db_'+str(x)+'.txt', 'w')
            db_file.write(response.text)
            db_file.close()
            size = len([len(item) for item in json.loads(response.text)])
            x += size
    print('Knowledge-base updated!')
    return None

def add_items(items):
    for item in items:
        assert (item['question'])
        assert (item['answer'])
        assert (item['relation'])
        assert (item['context'])
        assert (item['domains'])
        assert (item['c1'])
        assert (item['c2'])

    headers = {"content-type": "application/json"}
    params = {"key": key}
    url = kdb_url + 'add_items'

    response = requests.post(url, params = params, headers = headers, data = ujson.dumps(items))

    return None