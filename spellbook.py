import dataloaders
import difflib

class Spellbook():
    def __init__(self):
        self.build_spellbook()
            
    def build_spellbook(self):
        self.spells=[Spell.from_json(spell) for spell in dataloaders.get_spells()]
        self.names=[spell.name for spell in self.spells]
        self._names=[name.lower() for name in self.names] # Used to match queries through difflib

    def get_spell(self,query):
        target=difflib.get_close_matches(query.lower(),self._names,1)
        if target:
            target=self.names[self._names.index(target[0])] # Get the actual name of the spell
        else:
            return None

        for spell in self.spells:
            if spell.name==target:
                return spell
        return None

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
