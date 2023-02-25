import roll

import char
import cli


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

    def attack(self, template, character):
        print(roll.rolls_string(character.roll(template)))

    def list(self, character):
        cli.print_list("Attacks", self.templates)
        return (
            "func",
            [
                (lambda i: lambda: self.attack(self.templates[i], character))(i)
                for i in range(len(self.templates))
            ],
        )

    def list_deletes(self):
        cli.print_list("Delete attack", self.templates)
        return (
            "func",
            [
                (lambda i: lambda: self.templates.remove(self.templates[i]))(i)
                for i in range(len(self.templates))
            ],
        )

    def to_json(self):
        return {"templates": self.templates}

    @staticmethod
    def from_json(data):
        return Attacks(data["templates"])
