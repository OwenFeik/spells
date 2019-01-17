import json
import difflib

class Spellbook():
    def __init__(self):
        self.build_spellbook()
            
    def build_spellbook(self):
        with open('spells.json','r') as f:
            data=json.load(f)
        self.spells={i:[] for i in range(0,10)}
        for i in range(0,10):
            for spell in data[str(i)]:
                self.spells[i].append(Spell.from_json(spell))

    def get_spell(self,query):
        names=[]
        for i in range(0,10):
            names.extend([spell.name for spell in self.spells[i]])
        try:
            target=difflib.get_close_matches(query,names,1)[0]
        except IndexError:
            return None
        for i in range(0,10):
            for spell in self.spells[i]:
                if spell.name==target:
                    return spell
        


class Spell():
    def __init__(self,name,levl,cast,rnge,cmpn,durn,desc):
        self.name=name
        self.levl=levl
        self.cast=cast
        self.rnge=rnge
        self.cmpn=cmpn
        self.durn=durn
        self.desc=desc

    def to_json(self):
        return {
            'name':self.name,
            'level':self.levl,
            'cast':self.cast,
            'range':self.rnge,
            'components':self.cmpn,
            'duration':self.durn,
            'description':self.desc
        }

    @staticmethod
    def from_json(data):
        name=data.get('name')
        levl=data.get('level')
        cast=data.get('cast')
        rnge=data.get('range')
        cmpn=data.get('components')
        durn=data.get('duration')
        desc=data.get('description')
        return Spell(name,levl,cast,rnge,cmpn,durn,desc)
