import os
import json

if __name__ == '__main__':
    source_file = 'source'
    weights_file = ''
    config_dict = dict()
    config_dict['source_file'] = source_file
    config_dict['weights_file'] = weights_file
    print(config_dict)

    with open("config_json.json", "w", encoding='utf-8') as config:
        config.write(json.dumps(config_dict, ensure_ascii=False))


    config = json.load(open("config_json.json", encoding='utf-8'))
    print(type(config))
    print(config['weights_file'], config['weights_file'])
    if config.get('weights_file'):
        print('112')

