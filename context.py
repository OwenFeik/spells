import dataloaders
import utilities
import cli
import char
import commands
import re

class Context():
    def __init__(self, spellbook, character = None):
        self.spellbook = spellbook
        self.character = character
        self.raw_text = ''
        self.arg_text = ''
        self.command = ''
        self.args = []
        self.option_mode = ''
        self.options = []
        self.previous_roll = []
        self.previous_roll_die = None

    def get_input(self, message = '', string = None):
        try:
            if string:
                self.raw_text = string
            else:
                self.raw_text = input(f'{message}> ')
            self.arg_text = self.raw_text.strip().replace(',', '')
            self.command, *self.args = [arg for arg in self.arg_text.split(' ') if arg != '']
            self.raw_text = self.raw_text.replace(self.command, '', 1).strip()
            self.arg_text = self.arg_text.replace(self.command, '', 1).strip()
        
        except Exception as e:
            print(f'Ran into issue parsing input: {e}.')
            self.raw_text = ''
            self.arg_text = ''
            self.command = ''
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
            dataloaders.save_character(self.character)
            dataloaders.save_cache(self.character)
        else:
            dataloaders.save_cache()

    def update_options(self, option_tuple):
        self.option_mode, self.options = option_tuple

    def update_roll(self, roll_tuple):
        self.previous_roll, self.previous_roll_die = roll_tuple

    def character_check(self, new_char = False):
        if not self.character and new_char and cli.get_decision('No current character, which is required for this action. Create a temporary character?'):
            self.character = char.Char()
            print('Rename your character with "rename <name>" and add levels with "levelup".')              

        return True if self.character else False

    def spellbook_check(self):
        return True if self.spellbook else False

    def handle_command(self):
        try:
            if self.command.isnumeric():
                index = int(self.command) - 1
                if self.options and index < len(self.options):
                    option = self.options[index]
                    if self.option_mode == 'spell':
                        self.get_input(string = f'info {option}')
                    elif self.option_mode == 'char':
                        self.get_input(string = f'char {option}')
                    elif self.option_mode == 'roll':
                        self.get_input(string = option)
                else:
                    print('That option isn\'t available right now.')
                    return

            if self.command in commands.mapping:
                commands.mapping[self.command](self)
            elif self.character and self.command in self.character.trackers:
                if self.args:
                    print(self.character.trackers[self.command].handle_command(self.args))
                else:
                    print(self.character.trackers[self.command])
            elif re.match(r'^[0-9]*d[0-9]+$', self.command):
                self.update_roll(utilities.parse_roll(self.command))
            else:
                suggestion = utilities.suggest_command(self.command)
                if suggestion:
                    print(f'Unknown command: {self.command}. Perhaps you meant "{suggestion}".')
                else:
                    print(f'Unknown command: {self.command}.')
        except Exception as e:
            print(f'Ran into issue executing command: {e}.')
