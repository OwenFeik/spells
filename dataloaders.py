import json

def get_spellslots(clss,level):
    with open('resources/spellslots.json','r') as f:
        return json.load(f).get(clss).get(str(level))
        
def get_spells(clss):
    with open('resources/spells.json','r') as f:
        return json.load(f).get(clss)
        
def load_character(name):
    with open(f'saves/{name}.json','r') as f:
        return  json.load(f)