import re # Check command patterns
from char import Char
from spellbook import Spellbook
from cli import print_spell, print_prepped, print_chars, print_spellslots
from dataloaders import load_character, save_character, delete_character
from utilities import clean_string, clear_screen, parse_roll

c=None # Current player character

try:
    try:
        sb = Spellbook() # Utility for retrieving spell information
    except ValueError:
        print('Spellbook file corrupted. No Spellbook available.')
except FileNotFoundError:
    print('Warning: No Spellbook available.')

opt=[] # Options which persist after certain functions

while True:
    
    try:
        inpt = [clean_string(string) for string in input('> ').split(' ') if string != '']
        command = inpt.pop(0).lower()
        args = inpt
    except:
        command = ''
        args = []

    try:
        if command.isnumeric(): # Handle options
            index = int(command) - 1
            if opt and index < len(opt[1]):
                if opt[0] == 'spell':
                    args = [opt[1][index]]
                    command = 'info'
                elif opt[0] == 'char':
                    args = [opt[1][index]]
                    command = 'char'
                elif opt[0] == 'class':
                    if opt[2] == 'cast':
                        c.cast_spell(sb.get_spell(opt[3]), opt[1][index])
                    elif opt[2] == 'prep':
                        c.prepare_spell(sb.get_spell(opt[3]), opt[1][index])
                    elif opt[2] == 'level_up':
                        c.level_up(opt[1][index])
            else:
                print('That option isn\'t available right now.')
        
        if command=='exit':
            if c:
                save_character(c)
            raise SystemExit
        elif command in ['info','i']:
            arg=' '.join(args)
            spell=sb.get_spell(arg)
            if spell:
                print_spell(spell)
            else:
                print('Sorry, I couldn\'t find that spell.')
        elif command=='roll':
            parse_roll(args[0])
        elif re.match('[0-9]+d[0-9]+$',command):
            parse_roll(command)
        elif command=='chars':
            opt=print_chars()
        elif command=='delchar':
            delete_character(args[0])
        elif command in ['clear','cls']:
            clear_screen()
        elif command in ['char','ch']:
            if args:
                try:
                    try:
                        if sb:
                            data=load_character(args[0].lower())
                            data.update({'sb':sb})
                            c=Char.from_json(data)
                        else:
                            c=Char.from_json(load_character(args[0].lower()))
                        print(f'Character loaded: {c.name}.')
                    except ValueError:
                        print(f'Ran into issue loading character {args[0]}.')
                except FileNotFoundError:
                    print(f'No character {args[0]} found.')
            else:
                if c:
                    print(f'Current character: {c.name}.')
                else:
                    c=Char.from_wizard()
        elif command in ['prep','p']:
            if c:
                spell=sb.get_spell(' '.join(args))
                if spell:
                    opt=c.prepare_spell(spell)
                else:
                    print('Sorry, I couldn\'t find that spell.')
            else:
                print('To prepare spells, start a character with "char".')
        elif command in ['prepped','prepared','pd']:
            if c:
                opt=print_prepped(c)
            else:
                print('To prepare spells, start a character with "char".')
        elif command in ['cast','c']:
            if c:
                spell=sb.get_spell(' '.join(args))
                if spell:
                    opt=c.cast_spell(spell)
                else:
                    print(f'No spell {args[0]} found.')
            else:
                print('To cast spells, start a character with "char".')
        elif command=='slots':
            if c:
                print_spellslots(c)
            else:
                print('No current character.')
        elif command=='rename':
            c.name=args[0]
        elif command=='rest':
            if c:
                c.long_rest()
            else:
                print('To rest, start or load a character with "char".')
        elif command=='levelup' or (command=='level' and args[0]=='up'):
            if args and args[0] == 'up':
                del args[0]
            if args:
                c.level_up(args[0])
            else:
                opt = c.level_up()
        elif command in ['sorcerer','sorc','sorcery']:
            if c:
                klasse=c.has_class('sorcerer')
                if klasse:
                    klasse.handle_special_action(args)
                else:
                    print('This character is not a sorcerer.')
            else:
                print('Create a Sorcerer with "char" to use this command.')

    except Exception as e:
        print(f'Ran into a problem with that command: {e}')
