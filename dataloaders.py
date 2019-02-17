import json
import os

def get_spellslots(clss,level):
    with open('resources/spellslots.json','r') as f:
        return json.load(f).get(clss).get(str(level))
        
def get_spells():
    with open('resources/spells.json','r') as f:
        return json.load(f)

def get_spell(spell):
    return get_spells().get(spell)
        
def load_character(name):
    with open(f'saves/{name}.json','r') as f:
        return  json.load(f)

def current_chars():
    saves=os.listdir('saves')
    chars=[]
    for save in saves:
        if '.json' in save:
            with open(f'saves/{save}','r') as f:
                chars.append(json.load(f))
    return chars
