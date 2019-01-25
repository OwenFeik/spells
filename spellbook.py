from dataloaders import get_spells
import difflib

class Spellbook():
    def __init__(self,clss):
        self.clss=clss
        self.build_spellbook()
            
    def build_spellbook(self):
        self.spells=[Spell.from_json(spell) for spell in get_spells(self.clss)]
        self.names=[spell.name for spell in self.spells]

    def get_spell(self,query):
        try:
            target=difflib.get_close_matches(query,self.names,1)[0]
        except IndexError:
            return None

        for spell in self.spells:
            if spell.name==target:
                return spell
        
    def get_spells(self,queries):
        spells=[]
        for spell in queries:
            spells.append(self.get_spell(spell))
        return spells

class Spell():
    def __init__(self,name,school,level,cast,rnge,components,duration,desc):
        self.name=name
        self.school=school
        self.level=level
        self.cast=cast
        self.rnge=rnge
        self.components=components
        self.duration=duration
        self.desc=desc

    def __str__(self):
        return f'\n{self.name} | {self.school}\n{self.cast} | {self.rnge}\n{self.components} | {self.duration}\n\n{self.desc}\n'

    def to_json(self):
        return {
            'name':self.name,
            'school':self.school,
            'level':self.level,
            'cast':self.cast,
            'range':self.rnge,
            'components':self.components,
            'duration':self.duration,
            'description':self.desc
        }

    @staticmethod
    def from_json(data):
        name=data.get('name')
        school=data.get('school')
        level=data.get('level')
        cast=data.get('cast')
        rnge=data.get('range')
        components=data.get('components')
        duration=data.get('duration')
        desc=data.get('description')
        
        return Spell(name,school,level,cast,rnge,components,duration,desc)
