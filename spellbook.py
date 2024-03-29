import difflib

import cli
import dataloaders
import utilities


class Spellbook:
    def __init__(self):
        self.build_spellbook()

    def build_spellbook(self):
        try:
            self.spells = {
                spell["name"]: Spell.from_json(spell)
                for spell in dataloaders.get_spells()
            }

            alt_names = {}
            for spell in self.spells.values():
                if spell.alt_names:
                    for name in spell.alt_names:
                        alt_names[name] = spell
            self.spells.update(alt_names)

            self.names = list(self.spells.keys())

            # Used to match queries through difflib
            self._names = [name.lower() for name in self.names]
        except Exception as e:
            raise ValueError from e

    def handle_query(self, query):
        queries = utilities.parse_spell_query(query)

        results = []
        for spell in self.spells.values():
            for q in queries:
                try:
                    if not queries[q] in str(getattr(spell, q)).lower():
                        break
                except AttributeError as e:
                    raise ValueError(f"Invalid query term: {q}.") from e
            else:
                results.append(spell)

        return results

    def get_spell(self, query):
        target = difflib.get_close_matches(query.lower(), self._names, 1)
        if target:
            return self.spells[self.names[self._names.index(target[0])]]
        else:
            return None

    def get_spells(self, queries):
        spells = []
        for spell in queries:
            spells.append(self.get_spell(spell))
        return spells

    def add_spell(self, spell):
        if spell.name in self.names and not cli.get_decision(
            f"{spell.name} is already in your spellbook."
            " Would you like to replace it?"
        ):
            return

        self.spells[spell.name] = spell

        if spell.name not in self.names:
            self.names.append(spell.name)
            self._names.append(spell.name)

    def add_spells(self, spells):
        for spell in spells:
            self.add_spell(spell)

    def get_spells_json(self):
        unique_check = []
        spells = []
        for spell in self.spells.values():
            if not spell in unique_check:
                spells.append(spell.to_json())
                unique_check.append(spell)

        return sorted(spells, key=lambda sp: sp["name"])


class Spell:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "N/A")
        self.school = kwargs.get("school", "N/A")
        self.level = kwargs.get("level", -1)
        self.cast = kwargs.get("cast", "N/A")
        self.range = kwargs.get("range", "N/A")
        self.components = kwargs.get("components", "N/A")
        self.duration = kwargs.get("duration", "N/A")
        self.desc = kwargs.get("description", "N/A")
        self.ritual = kwargs.get("ritual", False)
        self.classes = kwargs.get("classes", [])
        self.subclasses = kwargs.get("subclasses", [])
        self.alt_names = kwargs.get("alt_names", [])

    def __str__(self):
        return f'\n{self.name} | {self.school}\
            \n{self.cast} | {self.range}{" | Ritual" if self.ritual else ""}\n\
            {self.components} | {self.duration}\n\n{self.desc}\n'

    def to_json(self):
        return {
            "name": self.name,
            "school": self.school,
            "level": self.level,
            "cast": self.cast,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "description": self.desc,
            "ritual": self.ritual,
            "classes": self.classes,
            "subclasses": self.subclasses,
            "alt_names": self.alt_names,
        }

    @staticmethod
    def from_json(data):
        return Spell(**data)
