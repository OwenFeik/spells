import roll

import cli
import utilities

from .stats import Stats


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
