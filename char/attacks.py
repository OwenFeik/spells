import roll

import char
import cli
import utilities


class Attacks:
    def __init__(self, templates=None):
        self.templates = templates if templates else []

    def add_template(self, template, character):
        template = template.strip()
        if not template:
            return "Usage: attack <roll>"
        try:
            roll.get_rolls(self.apply_template(template, character))
        except ValueError as e:
            return f"Invalid attack: {e}"
        self.templates.append(template)
        return "Added attack."

    def apply_template(self, template, character):
        template = template.lower()
        for stat in char.Stats.DND_STATS:
            mod = character.stats.mod(stat)
            template = template.replace(stat.lower(), str(mod))
        return template.replace("prof", str(character.proficiency_bonus))

    def attack(self, template, character):
        print(
            roll.rolls_string(
                character.roll(self.apply_template(template, character))
            )
        )

    def list(self, character):
        cli.print_list("Attacks", self.templates)
        return (
            "func",
            [
                lambda: self.attack(template, character)
                for template in self.templates
            ],
        )

    def list_deletes(self):
        cli.print_list("Delete attack", self.templates)
        return (
            "func",
            [
                lambda: self.templates.remove(template)
                for template in self.templates
            ],
        )

    def to_json(self):
        return {"templates": self.templates}

    @staticmethod
    def from_json(data):
        return Attacks(data["templates"])
