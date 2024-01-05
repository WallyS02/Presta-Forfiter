import os
import json
import urllib.request


bad_characters = ['*', '/']


def forbidden_characters(variable):
    characters = ['', '\n', '*']
    if variable in characters:
        return False
    else:
        return True


def prepare_name(name):
    split_name = name.split(' ')
    filtered_name = filter(forbidden_characters, split_name)
    prepared_name = str()
    for word in filtered_name:
        prepared_name += word + '-'
    for bad_character in bad_characters:
        prepared_name = prepared_name.replace(bad_character, '')
    return prepared_name.rstrip(prepared_name[-1])


def download_photos(filename):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), 'r', encoding='utf-8') as file:
        file_elements = json.load(file)
    for file_element in file_elements:
        prepared_name = prepare_name(file_element['name'])
        path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scrapped_data/images'), prepared_name + '-BIG.jpg')
        if not os.path.exists(path):
            if file_element['big-photo']:
                urllib.request.urlretrieve(file_element['big-photo'], path)
        path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scrapped_data/images'), prepared_name + '.jpg')
        if not os.path.exists(path):
            if file_element['big-photo']:
                urllib.request.urlretrieve(file_element['photo'], path)


download_photos('..\\scrapped_data\\products.json')
