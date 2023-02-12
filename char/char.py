import roll

import constants
import cli
import tracker
import utilities

from .attacks import Attacks
from .rollhist import RollHistory
from .skills import Skills
from .stats import Stats


class Char:
    TRACKER_COLLECTION_NAME = "Trackers"

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "temp")
        self.klasses = kwargs.get("classes", [])
        self.skills = kwargs.get("skills", Skills())
        self.spell_slots_used = kwargs.get("spell_slots_used", [0] * 9)

        if "prepared" in kwargs:
            if kwargs.get("sb"):
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

        self.trackers = kwargs.get(
            "trackers",
            tracker.TrackerCollection(name=Char.TRACKER_COLLECTION_NAME),
        )
        self._stats = kwargs.get("stats")
        self.notes = kwargs.get("notes", [])
        self.roll_history = kwargs.get("roll_history", RollHistory())
        self.attacks = kwargs.get("attacks", Attacks())

    def __str__(self):
        klasse_string = ", ".join(
            [
                f'{utilities.capitalise(k["name"])} {k["level"]}'
                for k in self.klasses
            ]
        )
        return f"{utilities.capitalise(self.name)} | {klasse_string}"

    @property
    def stats(self):
        if self._stats is None:
            if cli.get_decision(
                f"{self.name} has no stats, which are required to"
                " perform this action. Create now?"
            ):
                self._stats = Stats.from_wizard()
            else:
                raise AttributeError(f"{self.name} has no stats")
        return self._stats

    @property
    def caster_level(self):
        return sum([int(k["caster"] * k["level"]) for k in self.klasses])

    @property
    def level(self):
        return sum(k["level"] for k in self.klasses)

    @property
    def proficiency_bonus(self):
        return (self.level - 1) // 4 + 2

    @property
    def spell_slots(self):
        return constants.SPELLSLOTS[self.caster_level]

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
        print(self.trackers)

    def long_rest(self):
        self.spell_slots_used = [0] * 9
        return self.trackers.rest()

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
            if len(self.klasses) == 1:
                (level := self.klasses[0])["level"] += 1
            else:
                klasse = cli.get_choice(
                    "In which class was a level gained?",
                    [k["name"] for k in self.klasses],
                )
                (level := [k for k in self.klasses if k["name"] == klasse][0])[
                    "level"
                ] += 1
        else:
            klasse = cli.get_input("In which class was a level gained?").lower()

            for k in self.klasses:
                if k["name"] == klasse:
                    k["level"] += 1
                    level = k
                    break
            else:
                self.klasses.append(
                    (level := Char.get_klasse_detail(klasse, 1))
                )

        if message := self.trackers.level_up(self, level):
            print(message)

    def add_note(self, note):
        self.notes.append(note)

    def remove_note(self, index):
        self.notes = self.notes[:index] + self.notes[index + 1 :]

    def replace_note(self, index, new):
        self.remove_note(index)
        self.notes.insert(index, new)

    def move_note_up(self, index):
        if index > 0:
            ns = self.notes
            ns[index - 1], ns[index] = ns[index], ns[index - 1]

    def move_note_down(self, index):
        if index < len(self.notes) - 1:
            ns = self.notes
            ns[index + 1], ns[index] = ns[index], ns[index + 1]

    def roll(self, string, single=False):
        if single:
            r = roll.get_roll(string)
            self.roll_history.log_roll(r)
            return r
        else:
            rolls = roll.get_rolls(string)
            for r in rolls:
                self.roll_history.log_roll(r)
            return rolls

    def to_json(self):
        return {
            "name": self.name,
            "classes": self.klasses,
            "spell_slots_used": self.spell_slots_used,
            "prepared": [s.name for s in self.prepared],
            "trackers": self.trackers.to_json(),
            "skills": self.skills.to_json(),
            "stats": self._stats.to_json() if self._stats is not None else None,
            "notes": self.notes,
            "roll_history": self.roll_history.to_json(),
            "attacks": self.attacks.to_json(),
        }

    @staticmethod
    def from_json(data):
        try:
            if "trackers" in data:
                # Older versions used a list instead of a TrackerCollection to
                # store trackers. Here we adapt a list to a TrackerCollection
                # instance.
                if isinstance(data["trackers"], list):
                    trackers = {t["name"]: t for t in data["trackers"]}
                    data["trackers"] = tracker.from_json(
                        {
                            "type": "TrackerCollection",
                            "name": Char.TRACKER_COLLECTION_NAME,
                            "quantity": trackers,
                        }
                    )
                else:
                    data["trackers"] = tracker.from_json(data["trackers"])
        except Exception as e:
            print(
                f"Failed to parse tracker information (error: {e})."
                " Defaulting to empty collection."
            )
            del data["trackers"]

        try:
            if data.get("stats") is not None:
                data["stats"] = Stats.from_json(data["stats"])
        except:
            print("Failed to parse stats information. Dropping stats.")
            del data["stats"]

        if "skills" in data:
            data["skills"] = Skills.from_json(data["skills"])

        if "roll_history" in data:
            data["roll_history"] = RollHistory.from_json(data["roll_history"])

        if "attacks" in data:
            data["attacks"] = Attacks.from_json(data["attacks"])

        return Char(**data)

    @staticmethod
    def get_klasse_detail(name, level):
        name = name.lower()

        CASTER_TYPE_NAMES = ["non", "half", "full"]
        if (caster_type := constants.CASTER_TYPES.get(name)) is None:
            caster_type = constants.CASTER_TYPES[
                cli.get_choice(
                    f"Class {name} not found. What type of caster is it?",
                    CASTER_TYPE_NAMES,
                )
            ]

        if (hit_die := constants.KLASSE_HIT_DIE.get(name)) is None:
            hit_die = cli.get_choice(
                f"What hit die does class {name} use?",
                [f"d{s}" for s in constants.HIT_DIE_SIZES],
                constants.HIT_DIE_SIZES,
            )

        if cli.get_decision(
            f"Confirm class {name} (d{hit_die}, "
            + CASTER_TYPE_NAMES[int(2 * caster_type)]
            + " caster)"
        ):
            return {
                "name": name,
                "level": level,
                "caster": caster_type,
                "hit_die": hit_die,
            }
        return None

    @staticmethod
    def klasses_wizard():
        prompt = "Enter your character's classes and levels:" " <class> <level>"
        PROMPT_DETAILED = (
            "Enter the character's classes and levels"
            ' e.g. "Cleric 1 wizard 2"'
        )

        klasses = []

        while True:
            inpt = cli.get_input(prompt, True)
            if len(inpt) % 2 == 0 and len(inpt) != 0:
                for i in range(0, len(inpt), 2):
                    if inpt[i + 1].isnumeric() and (
                        klasse := Char.get_klasse_detail(
                            inpt[i].lower(), int(inpt[i + 1])
                        )
                    ):
                        klasses.append(klasse)
                    else:
                        prompt = PROMPT_DETAILED
                        break
                else:
                    return klasses
            else:
                prompt = PROMPT_DETAILED

    @staticmethod
    def from_wizard():
        data = {
            "name": cli.get_input("What is you character's name?"),
            "classes": Char.klasses_wizard(),
        }

        if cli.get_decision("Create stats for this character?"):
            data["stats"] = Stats.from_wizard()

        return Char(**data)
