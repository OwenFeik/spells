import constants
import cli
import tracker
import utilities


class Char:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "temp")
        self.klasses = kwargs.get("classes", [])
        self.spell_slots_used = kwargs.get("spell_slots_used", [0] * 9)
        if "prepared" in kwargs:
            if "sb" in kwargs:
                self.prepared = [
                    kwargs["sb"].get_spell(s)
                    for s in kwargs.get("prepared", [])
                ]
            else:
                print(
                    "Warning: no spellbook available,"
                    " some spellcasting functionality unavailable."
                )
        else:
            self.prepared = []
        self.trackers = kwargs.get("trackers", {})

    def __str__(self):
        klasse_string = ", ".join(
            [
                f'{utilities.capitalise(k["name"])} {k["level"]}'
                for k in self.klasses
            ]
        )
        return f"{utilities.capitalise(self.name)} | {klasse_string}"

    @property
    def caster_level(self):
        return sum([int(k["caster"] * k["level"]) for k in self.klasses])

    @property
    def spell_slots(self):
        return constants.spellslots[self.caster_level]

    def unused_slots(self, level):
        return self.spell_slots[level - 1] - self.spell_slots_used[level - 1]

    def print_spell_slots(self):
        out = "\nSpell Slots:"
        for i in range(0, 9):
            out += f"\n\t{utilities.level_prefix(i + 1)}: " + str(
                self.spell_slots[i] - self.spell_slots_used[i]
            )
        print(out + "\n")

    def print_trackers(self):
        print("\nTrackers:")
        for t in self.trackers:
            print(f"\t{str(self.trackers[t])}")
        print()

    def long_rest(self):
        self.spell_slots_used = [0] * 9
        for t in self.trackers.values():
            t.rest()

    def has_spell_slot(self, level):
        if level == 0:
            return True
        if self.spell_slots_used[level - 1] < self.spell_slots[level - 1]:
            return True
        else:
            return False

    def prepare_spell(self, spell):
        if spell in self.prepared:
            self.prepared.remove(spell)
            print(f"Forgot the spell {spell.name}.")
        else:
            self.prepared.append(spell)
            print(f"Learnt the spell {spell.name}.")

    def cast_spell(self, spell):
        if (
            spell in self.prepared
            or spell.school == "placeholder"
            or cli.get_decision(f"{spell.name} isn't prepared. Cast anyway?")
        ):
            if self.has_spell_slot(spell.level) or cli.get_decision(
                f"No level {spell.level} slots available. Cast anyway?"
            ):
                self.spell_slots_used[spell.level - 1] += 1
                print(
                    f"You cast {spell.name}. {self.unused_slots(spell.level)}"
                    f" level {spell.level} slots remaining."
                )
        elif spell.level == 0:
            pass
        else:
            print(f"{spell.name} not prepared.")

    def level_up(self, klasse=None):
        if self.klasses and cli.get_decision(
            "Add level to already present class?"
        ):
            klasse = cli.get_choice(
                "In which class was a level gained?",
                [k["name"] for k in self.klasses],
            )
            [k for k in self.klasses if k["name"] == klasse][0]["level"] += 1
        else:
            klasse = input("In which class was a level gained? > ")
            if klasse in constants.caster_types:
                caster_type = klasse
            else:
                have_type = False
                while not have_type:
                    caster_type = input(
                        "Is this class a half (h), full (f) or"
                        " non (n) caster? > "
                    )
                    if caster_type.lower() in ["half", "full", "non"]:
                        have_type = True
                    elif caster_type in ["h", "f", "n"]:
                        caster_type = {"h": "half", "f": "full", "n": "non"}[
                            caster_type
                        ]
                        have_type = True
                    elif not cli.get_decision("Inadmissable input. Retry?"):
                        return

            self.klasses.append(
                {
                    "name": klasse,
                    "level": 1,
                    "caster": constants.caster_types[caster_type],
                }
            )

    def to_json(self):
        return {
            "name": self.name,
            "classes": self.klasses,
            "spell_slots_used": self.spell_slots_used,
            "prepared": [s.name for s in self.prepared],
            "trackers": [t.to_json() for t in self.trackers.values()],
        }

    @staticmethod
    def from_json(data):
        if "trackers" in data:
            data["trackers"] = {
                t["name"]: tracker.from_json(t) for t in data["trackers"]
            }
        return Char(**data)

    @staticmethod
    def from_wizard():
        data = {
            "name": input("What is you character's name? > "),
            "classes": [],
        }

        classes_done = False
        prompt = (
            "Enter your character's classes and levels:"
            " <class> <level> <class> <level> "
        )
        while not classes_done:
            inpt = cli.get_input(prompt)
            if len(inpt) % 2 == 0 and len(inpt) != 0:
                for i in range(0, len(inpt), 2):
                    klasse = inpt[i].lower()
                    if klasse not in constants.caster_types:
                        caster_type = cli.get_choice(
                            f"Class {klasse} not found."
                            "What type of caster is it?",
                            ["full", "half", "non"],
                        )
                        if (
                            input(
                                f"Confirm class {klasse} ({caster_type}"
                                " caster) (y/n) > "
                            ).strip()
                            != "y"
                        ):
                            prompt = (
                                "Enter your character's classes and"
                                " levels: <class> <level> <class> <level> "
                            )
                            break
                    else:
                        caster_type = klasse

                    if inpt[i + 1].isnumeric():
                        data["classes"].append(
                            {
                                "name": inpt[i],
                                "level": int(inpt[i + 1]),
                                "caster": constants.caster_types[caster_type],
                            }
                        )
                    else:
                        prompt = (
                            "Enter the character's classes and levels:"
                            ' e.g. "Cleric 1 wizard 2" > '
                        )
                else:
                    classes_done = True

            else:
                prompt = (
                    "Enter the characters classes and levels:"
                    ' e.g. "Cleric 1 wizard 2" > '
                )

        return Char(**data)
