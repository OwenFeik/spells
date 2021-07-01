import traceback

import roll

import char
import cli
import commands
import dataloaders
import tracker
import utilities


class Context:
    def __init__(self, spellbook, config, character=None):
        self.spellbook = spellbook
        self.config = config
        self.character = character
        self.save_file = ""
        self.raw_text = ""
        self.arg_text = ""
        self.command = ""
        self.args = []
        self.option_mode = ""
        self.options = []
        self.previous_roll = None

    def get_input(self, message="", string=None):
        try:
            if string:
                self.raw_text = string.strip()
            else:
                self.raw_text = input(f"{message}{cli.PS}").strip()

            if not self.raw_text:
                self.arg_text = ""
                self.command = ""
                self.args = []
            else:
                self.arg_text = self.raw_text.replace(",", "")
                self.command, *self.args = self.arg_text.split()
                self.arg_text = self.arg_text.replace(
                    self.command, "", 1
                ).strip()
        except Exception as e:
            print(f"Ran into issue parsing input: {e}.")
            if self.config["print_stack_traces"]:
                traceback.print_exc()
            self.raw_text = ""
            self.arg_text = ""
            self.command = ""
            self.args = []

    def get_arg(self, index):
        try:
            return self.args[index]
        except IndexError:
            return None

    def arg_count(self):
        return len(self.args)

    def has_args(self):
        return self.arg_count() != 0

    def save(self):
        if self.character:
            self.save_file = dataloaders.save_character(
                self.character, self.save_file
            )
            dataloaders.save_cache(self.save_file)
        else:
            dataloaders.save_cache()
        dataloaders.save_config(self.config)

    def update_options(self, option_tuple):
        if option_tuple is None:
            return

        option_mode, options = option_tuple
        if options:
            self.option_mode, self.options = option_mode, options

    def update_roll(self, new_roll):
        self.previous_roll = new_roll

    def character_check(self, new_char=False):
        if (
            not self.character
            and new_char
            and cli.get_decision(
                "No current character, which is required for this action. "
                " Create a temporary character?"
            )
        ):

            self.character = char.Char()
            print(
                'Rename your character with "rename <name>" and add '
                'levels with "levelup".'
            )

        return True if self.character else False

    def set_char(self, char, save_check=False):
        if (
            save_check
            and self.character_check()
            and cli.get_decision(
                "Current character: "
                f"{self.character.name}. Save this character?"
            )
        ):
            self.save()

        self.character = char
        self.save_file = ""

    # breadth first search of tracker tree to find tracker with name
    def get_tracker(self, name=None, root=None, names=None):
        if not self.character_check(True):
            return None

        if names is None:
            if name:
                names = tracker.TrackerCollection.expand_name(name)
            else:
                return None

        try:
            target = names[-1]
            current = names[0]
        except IndexError:
            return None

        to_visit = [root if root else self.character.trackers]
        while to_visit:
            for tc in to_visit[:]:
                to_visit.remove(tc)
                if current in tc.trackers:
                    if current == target:
                        return tc.trackers[current]
                    else:
                        return self.get_tracker(
                            root=tc.trackers[current], names=names[1:]
                        )

                for t in tc.trackers.values():
                    if isinstance(t, tracker.TrackerCollection):
                        to_visit.append(t)
        return None

    def spellbook_check(self):
        return True if self.spellbook else False

    def handle_command(self):
        try:
            if not self.command:
                return

            if self.command.isnumeric() and len(self.args) == 0:
                index = int(self.command) - 1
                if self.options and 0 <= index < len(self.options):
                    option = self.options[index]
                    if self.option_mode == "spell":
                        self.get_input(string=f"info {option}")
                    elif self.option_mode == "char":
                        self.get_input(string=f"char {option}")
                    elif self.option_mode == "roll":
                        self.get_input(string=option)
                    elif self.option_mode == "note":
                        self.get_input(string=f"note {self.command}")
                    elif self.option_mode == "setting":
                        self.get_input(string=f"settings {option}")
                    elif self.option_mode == "func":
                        option()
                        return
                else:
                    print("That option isn't available right now.")
                    return

            if self.command in commands.mapping:
                commands.mapping[self.command](self)
                return
            elif (t := self.get_tracker(self.command)) :
                if self.args:
                    print(t.handle_command(self))
                else:
                    print(t)
                return

            rolls = roll.get_rolls(self.raw_text)
            if rolls:
                self.update_roll(rolls[-1])
                print(roll.rolls_string(rolls))
            else:
                suggestion = utilities.suggest_command(
                    self.command, commands.mapping.keys()
                )
                if suggestion:
                    print(
                        f"Unknown command: {self.command}. "
                        + f'Perhaps you meant "{suggestion}".'
                    )
                else:
                    print(f"Unknown command: {self.command}.")
        except Exception as e:
            print(f"Ran into issue executing command: {e}.")
            if self.config["print_stack_traces"]:
                traceback.print_exc()
