import dataloaders
import difflib
import utilities

class Spellbook():
    def __init__(self):
        self.build_spellbook()
            
    def build_spellbook(self):
        try:
            self.spells = {spell['name']: Spell.from_json(spell) \
                for spell in dataloaders.get_spells()}

            alt_names = {}
            for spell in self.spells.values():
                if spell.alt_names:
                    for name in spell.alt_names:
                        alt_names[name] = spell
            self.spells.update(alt_names)

            self.names = list(self.spells.keys())
            self._names = [name.lower() for name in self.names] # Used to match queries through difflib
        except:
            raise ValueError

    def handle_query(self, query):
        queries = utilities.parse_spell_query(query)

        results = []
        for spell in self.spells.values():
            for q in queries:
                try:
                    if not queries[q] in str(getattr(spell, q)).lower():
                        break
                except AttributeError:
                    raise ValueError(f'Invalid query term: {q}.')
            else:
                results.append(spell)
        
        return results

    def get_spell(self,query):
        target = difflib.get_close_matches(query.lower(), self._names, 1)
        if target:
            return self.spells[self.names[self._names.index(target[0])]]
        else:
            return None

    def get_spells(self,queries):
        spells = []
        for spell in queries:
            spells.append(self.get_spell(spell))
        return spells

class Spell():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'N/A')
        self.school = kwargs.get('school', 'N/A')
        self.level = kwargs.get('level', -1)
        self.cast = kwargs.get('cast', 'N/A')
        self.rnge = kwargs.get('range', 'N/A')
        self.components = kwargs.get('components', 'N/A')
        self.duration = kwargs.get('duration', 'N/A')
        self.desc = kwargs.get('description', 'N/A')
        self.ritual = kwargs.get('ritual', False)
        self.classes = kwargs.get('classes', [])
        self.subclasses = kwargs.get('subclasses', [])
        self.alt_names = kwargs.get('alt_names', [])

    def __str__(self):
        return f'\n{self.name} | {self.school}\
            \n{self.cast} | {self.rnge}{" | Ritual" if self.ritual else ""}\n\
            {self.components} | {self.duration}\n\n{self.desc}\n'

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
            'ritual': self.ritual,
            'classes': self.classes,
            'subclasses': self.subclasses,
            'alt_names': self.alt_names
        }

    @staticmethod
    def from_json(data):
        return Spell(**data)
