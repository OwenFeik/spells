import dataloaders
import difflib
import utilities

class Spellbook():
    def __init__(self):
        self.build_spellbook()
            
    def build_spellbook(self):
        try:
            self.spells=[Spell.from_json(spell) for spell in dataloaders.get_spells()]
            self.names=[spell.name for spell in self.spells]
            self._names=[name.lower() for name in self.names] # Used to match queries through difflib
        except:
            raise ValueError

    def handle_query(self, query):
        queries = utilities.parse_spell_query(query)

        results = []
        for spell in self.spells:
            for q in queries:
                if not queries[q] in str(getattr(spell, q)).lower():
                    break
            else:
                results.append(spell)
        
        return results

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
    def __init__(self, name, school, level, cast, rnge, components, duration, desc, ritual):
        self.name = name
        self.school = school
        self.level = level
        self.cast = cast
        self.rnge = rnge
        self.components = components
        self.duration = duration
        self.desc = desc
        self.ritual = ritual

    def __str__(self):
        return f'\n{self.name} | {self.school}\n{self.cast} | {self.rnge}{" | Ritual" if self.ritual else ""}\n{self.components} | {self.duration}\n\n{self.desc}\n'

    def to_json(self):
        return {
            'name': self.name,
            'school': self.school,
            'level': self.level,
            'cast': self.cast,
            'range': self.rnge,
            'components': self.components,
            'duration': self.duration,
            'description': self.desc,
            'ritual': self.ritual
        }

    @staticmethod
    def from_json(data):
        name = data.get('name', 'N/A')
        school = data.get('school', 'N/A')
        level = data.get('level', -1)
        cast = data.get('cast', 'N/A')
        rnge = data.get('range', 'N/A')
        components = data.get('components', 'N/A')
        duration = data.get('duration', 'N/A')
        desc = data.get('description', 'N/A')
        ritual = data.get('ritual', False)
        
        return Spell(name, school, level, cast, rnge, components, duration, desc, ritual)
