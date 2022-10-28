import collections
import time

import roll

import constants
import cli
import tracker
import utilities


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


class Stats:
    STR = "str"
    DEX = "dex"
    CON = "con"
    INT = "int"
    WIS = "wis"
    CHA = "cha"
    DEFAULT_VALUE = 10
    DND_STATS = [STR, DEX, CON, INT, WIS, CHA]
    DEFAULT_ROLL_FORMAT = "4d6k3"

    def __init__(self, **kwargs):
        for stat in Stats.DND_STATS:
            setattr(self, stat, kwargs.get(stat, Stats.DEFAULT_VALUE))

    def __str__(self):
        return self.indented_string()

    def __getitem__(self, key):
        return getattr(self, key.lower())

    def mod(self, mod_name):
        return (self[mod_name.lower()] - 10) // 2

    def set_stat(self, stat, value):
        setattr(self, stat.lower(), value)

    def indented_string(self, title="Stats"):
        string = f"{title}:\n\t"
        string += "\n\t".join(
            f"{s.upper()}: {getattr(self, s)}" for s in Stats.DND_STATS
        )
        return string

    def update_stat_wizard(self):
        self.set_stat(
            cli.get_choice(
                "Update which stat?", [s.upper() for s in Stats.DND_STATS]
            ),
            cli.get_integer("New score", 10),
        )

    def to_json(self):
        return {s: getattr(self, s) for s in Stats.DND_STATS}

    @staticmethod
    def from_entry_wizard():
        stats = {}

        for stat in Stats.DND_STATS:
            stats[stat] = cli.get_integer(
                stat.upper() + " score", Stats.DEFAULT_VALUE
            )

        return Stats(**stats)

    @staticmethod
    def from_rolling_wizard():
        stats = {}
        remaining_stats = [s.upper() for s in Stats.DND_STATS]

        roll_format = cli.get_input(
            "Stat roll format", default=Stats.DEFAULT_ROLL_FORMAT
        )

        rolls = roll.get_rolls(f"{len(remaining_stats)} {roll_format}")
        print(f"\nYour rolls:\n{roll.rolls_string(rolls)}")
        scores = [str(r.total) for r in sorted(rolls, key=lambda r: r.total)]

        while len(remaining_stats) > 1:
            stat = cli.get_choice(
                "Choose a stat to assign a score to:", remaining_stats
            )
            remaining_stats.remove(stat)

            score = cli.get_choice(f"Choose a score for {stat}", scores)
            scores.remove(score)

            stats[stat.lower()] = int(score)
        stats[remaining_stats[0]] = scores[0]

        return Stats(**stats)

    @staticmethod
    def from_wizard():
        if cli.get_decision("Would you like to roll for stats?", False):
            return Stats.from_rolling_wizard()
        else:
            return Stats.from_entry_wizard()

    @staticmethod
    def from_json(data):
        return Stats(**data)


class Skill:
    PROF_CHAR = "+"
    EXP_CHAR = "!"
    NOT_CHAR = " "

    def __init__(
        self,
        name,
        stat,
        alt_names=None,
        allow_prefix=True,
        proficient=False,
        expertise=False,
        special=False,
    ):
        self.name = name
        self.stat = stat

        self.alt_names = alt_names or []
        self.name_lower = self.name.lower()
        if self.name_lower not in self.alt_names:
            self.alt_names.append(self.name_lower)

        self.allow_prefix = allow_prefix
        self.proficient = proficient
        self.expertise = expertise
        self.special = special

    def __repr__(self):
        return (
            f"<Skill name={self.name} stat={self.stat} "
            f"alt_names={self.alt_names} allow_prefix={self.allow_prefix} "
            f"proficient={self.proficient}>"
        )

    def __str__(self):
        return self.skill_str()

    def prof_str(self):
        prof_char = (
            (Skill.EXP_CHAR if self.expertise else Skill.PROF_CHAR)
            if self.proficient
            else Skill.NOT_CHAR
        )
        return f"[{prof_char}]"

    def mod_str(self, char):
        return utilities.mod_str(self.bonus(char))

    def skill_str(self, char=None):
        string = f"{self.prof_str()} {self.name}"
        if char:
            string += " " + self.mod_str(char)
        return string

    def bonus(self, char):
        bonus = char.stats.mod(self.stat)
        if self.proficient:
            bonus += char.proficiency_bonus
        if self.expertise:
            bonus += char.proficiency_bonus

        return bonus

    def check(self, char, adv_str=None):
        roll_string = f"d20"

        if adv_str:
            roll_string += adv_str

        bonus = self.bonus(char)

        if bonus > 0:
            roll_string += f" + {bonus}"
        elif bonus < 0:
            roll_string += f" {bonus}"

        return f"{self.name} check:\n" + roll.rolls_string(
            char.roll(roll_string)
        )

    def toggle_proficiency(self):
        self.proficient = not self.proficient
        if self.proficient:
            return f"Now proficient in {self.name}."
        else:
            self.expertise = False
            return f"No longer proficient in {self.name}."

    def toggle_expertise(self):
        if self.expertise:
            self.expertise = False
            if self.proficient:
                return f"Now only proficient in {self.name}."
            else:
                return f"No longer an expert in {self.name}."
        else:
            self.expertise = self.proficient = True
            return f"Now an expert in {self.name}."

    def to_json(self):
        return {
            "name": self.name,
            "stat": self.stat,
            "alt_names": self.alt_names,
            "allow_prefix": self.allow_prefix,
            "proficient": self.proficient,
            "expertise": self.expertise,
            "special": self.special,
        }

    @staticmethod
    def from_json(data):
        name = data.pop("name")
        stat = data.pop("stat")
        return Skill(name, stat, **data)

    @staticmethod
    def default_skills():
        return [
            Skill("Athletics", Stats.STR, alt_names=["aths"]),
            Skill("Acrobatics", Stats.DEX),
            Skill("Stealth", Stats.DEX),
            Skill("Sleight of Hand", Stats.DEX, alt_names=["soh"]),
            Skill("Arcana", Stats.INT),
            Skill("History", Stats.INT),
            Skill("Investigation", Stats.INT),
            Skill("Nature", Stats.INT),
            Skill("Religion", Stats.INT, alt_names=["rlg", "rgn"]),
            Skill("Animal Handling", Stats.WIS, alt_names=["ah"]),
            Skill("Insight", Stats.WIS),
            Skill("Medicine", Stats.WIS),
            Skill("Perception", Stats.WIS),
            Skill("Survival", Stats.WIS, alt_names=["sv"]),
            Skill("Deception", Stats.CHA),
            Skill("Intimidation", Stats.CHA),
            Skill("Performance", Stats.CHA),
            Skill("Persuasion", Stats.CHA),
        ]


class Skills:
    def __init__(self, skills=None):
        self.skills = skills or Skill.default_skills()

    def find_skill(self, name):
        name = name.lower()

        for skill in self.skills:
            if name in skill.alt_names:
                return skill

        return [
            skill for skill in self.skills if skill.name_lower.startswith(name)
        ] or None

    def skill_from_context(self, context):
        name = context.get_arg(0)
        if name is None:
            raise ValueError("Missing skill name argument.")

        result = self.find_skill(name)
        if result is None:
            raise ValueError(f'No skill matching name "{name}" exists.')

        # Returns either None, a list of matching Skills, or the single match
        if isinstance(result, list):
            if len(result) == 1:
                skill = result[0]
            else:
                skill = cli.get_choice(
                    "Multiple matching skills, which did you mean?",
                    [r.name for r in result],
                    result,
                )
        else:
            skill = result

        return skill

    def check(self, context):
        # Do this before parsing the result to save the user input if their
        # adv_str is invalid.
        adv_str = context.get_arg(1)
        if adv_str:
            adv_str = adv_str.lower()
            if not all(c in ["a", "d"] for c in adv_str):
                return 'Usage: "sc <skill_name> a" or "sc <skill_name> d".'

        if context.get_arg(0):
            stat = context.get_arg(0).upper()
            if stat.lower() in Stats.DND_STATS:
                mod = context.character.stats.mod(stat)
                roll_string = "d20" + (adv_str or "")
                if mod > 0:
                    roll_string += f" + {mod}"
                elif mod < 0:
                    roll_string += f" {mod}"

                return f"{stat} check:\n" + roll.rolls_string(
                    context.character.roll(roll_string)
                )

        try:
            return self.skill_from_context(context).check(
                context.character, adv_str
            )
        except ValueError as e:
            return str(e)

    def proficiency(self, context, expertise=False):
        try:
            skill = self.skill_from_context(context)
            if expertise:
                return skill.toggle_expertise()
            else:
                return skill.toggle_proficiency()
        except ValueError as e:
            return str(e)

    def skill_string(self, char):
        table = []

        def add_table_rows(skills):
            prev_stat = None
            for skill in skills:
                if skill.stat != prev_stat:
                    mod = utilities.mod_str(char.stats.mod(skill.stat))
                    table.append(f"{skill.stat.upper()} {mod}")
                    prev_stat = skill.stat
                table.append(
                    [skill.prof_str(), skill.name, skill.mod_str(char)]
                )

        normal = []
        special = []
        for skill in self.skills:
            if skill.special:
                special.append(skill)
            else:
                normal.append(skill)

        add_table_rows(normal)
        table.append("\nSpecial:")
        add_table_rows(special)

        return cli.format_table(table, "\t")

    def sort_skills(self):
        # Order skills in the traditional stat order, then alphabetically
        # within stat.
        stat_mapping = {
            Stats.STR: "0",
            Stats.DEX: "1",
            Stats.CON: "2",
            Stats.INT: "3",
            Stats.WIS: "4",
            Stats.CHA: "5",
        }

        self.skills.sort(
            key=lambda skill: stat_mapping[skill.stat] + skill.name.lower()
        )

    def new_skill(self, name):
        stat = cli.get_choice(
            f'Which stat is "{name}" associated with?',
            list(map(lambda s: s.upper(), Stats.DND_STATS)),
            Stats.DND_STATS,
        )
        special = cli.get_decision(
            "Display this skill seperately from the default set?"
        )
        self.skills.append(Skill(name, stat, special=special))
        self.sort_skills()
        return f'Added skill "{name}".'

    def delete_skill(self, context):
        try:
            skill = self.skill_from_context(context)
        except ValueError as e:
            return e

        self.skills.remove(skill)
        return f'Deleted skill "{skill.name}".'

    def add_skill_alt(self, context):
        try:
            skill = self.skill_from_context(context)
        except ValueError as e:
            return e

        alt = cli.get_input(f"Shortcut name for {skill.name}", split=True)[
            0
        ].lower()
        existing = self.find_skill(alt)
        if existing:
            return f'"{alt}" already points to "{existing.name}".'

        skill.alt_names.append(alt)
        return f'Added "{alt}" as a shortcut for "{skill.name}".'

    def to_json(self):
        return {"skills": [skill.to_json() for skill in self.skills]}

    @staticmethod
    def from_json(data):
        return Skills([Skill.from_json(skill) for skill in data["skills"]])


class RollHistory:
    DEFAULT_SIZES = [4, 6, 8, 10, 12, 20]

    def __init__(self, rolls=None):
        self.rolls = rolls or collections.defaultdict(lambda: [])

    def log_roll(self, robj):
        for (r, results) in robj.roll_info():
            _, die = r.split(roll.RollToken.SEPERATOR)
            self.rolls[int(die)].append((results, time.time()))

    def rolls_before(self, die, start_time):
        return [
            r
            for (results, t) in self.rolls[die]
            if t >= start_time
            for r in results
        ]

    def stat_string(self, start_time=0, die=None):
        table = []
        for die in die or RollHistory.DEFAULT_SIZES:
            rolls = self.rolls_before(die, start_time)
            if rolls:
                avg = round(sum(rolls) / len(rolls), 2)
                delta = round((avg - (1 + die) / 2), 2)
                delta_str = utilities.mod_str(delta) if delta else "(avg)"
            else:
                avg = 0.0
                delta_str = "(avg)"
            table.append(
                [
                    f"{roll.RollToken.SEPERATOR}{die}",
                    f"{str(len(rolls))} rolled",
                    str(avg),
                    delta_str,
                ]
            )
        return cli.format_table(table)

    def to_json(self):
        return {"rolls": self.rolls}

    @staticmethod
    def from_json(data):
        return RollHistory(
            collections.defaultdict(
                lambda: [], {int(k): v for k, v in data["rolls"].items()}
            )
        )
