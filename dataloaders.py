import json
import os # Check files in saves folder

def get_spellslots(clss,level):
    with open(f'resources/{clss}.json','r') as f:
        return json.load(f).get('spellslots').get(str(level))
        
def get_spells():
    with open('resources/spells.json','r') as f:
        return json.load(f)
       
def load_character(name):
    with open(f'saves/{name}.json','r') as f:
        return json.load(f)

def save_character(char):
    if not os.path.exists('saves'):
        os.mkdir('saves')
    with open(f'saves/{char.name.lower()}.json','w') as f:
        json.dump(char.to_json(),f,indent=4)

def current_chars():
    saves=os.listdir('saves')
    chars=[]
    for save in saves:
        if '.json' in save:
            with open(f'saves/{save}','r') as f:
                chars.append(json.load(f))
    return chars

def get_sorcery_points(level):
    with open(f'resources/sorcerer.json','r') as f:
        return json.load(f).get('sorc_points').get(str(level))
