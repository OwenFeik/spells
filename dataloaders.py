import json
import os # Check files in saves folder
import constants

def get_spellslots(level):
    return constants.spellslots[level]
        
def get_spells():
    with open('resources/spells.json','r') as f:
        return json.load(f)
       
def load_character(name):
    with open(f'saves/{name.lower()}.json','r') as f:
        return json.load(f)

def save_character(char):
    if not os.path.exists('saves'):
        os.mkdir('saves')

    with open(f'saves/{char.name.lower()}.json','w') as f:
        json.dump(char.to_json(), f, indent = 4)

def delete_character(char):
    if os.path.exists(f'saves/{char}.json'):
        os.remove(f'saves/{char}.json')
        print(f'Deleted character {char}.')
    else:
        print(f'No character "{char}" found.')

def current_chars():
    saves = os.listdir('saves')
    chars = []
    for save in saves:
        if '.json' in save:
            with open(f'saves/{save}','r') as f:
                chars.append(json.load(f))
    return chars

def get_cache():
    try:
        with open('resources/cache.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {
            'character': None
        }        

def save_cache(c = None):
    if not os.path.exists('resources'):
        os.mkdir('resources')

    with open('resources/cache.json', 'w') as f:
        json.dump({
            'character': c.name.lower() if c else None
        }, f)

def clear_cache():
    if os.path.exists('resources/cache.json'):
        os.remove('resources/cache.json')
