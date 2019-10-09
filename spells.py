import re # Check command patterns
from char import Char
from tracker import Tracker
from spellbook import Spellbook, Spell
from cli import print_spell, print_prepped, print_chars, print_spellslots, print_list, get_decision
from dataloaders import load_character, save_character, delete_character
from utilities import clean_string, clear_screen, parse_roll, level_prefix
from constants import commands

c = None # Current player character

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
        elif command in ['info', 'i']:
            arg = ' '.join(args)
            spell = sb.get_spell(arg)
            if spell:
                print_spell(spell)
            else:
                print('Sorry, I couldn\'t find that spell.')
        elif command in ['search', 's']:
            spells = sb.handle_query(' '.join(args))
            if spells:
                if len(spells) == 1:
                    print_spell(spells[0])
                else:
                    spell_names = [spell.name for spell in spells]
                    print_list('Results', spell_names)
                    opt = ['spell', spell_names]
            else:
                print('Couldn\'t find any spells matching that description.')
        elif command == 'roll':
            parse_roll(args[0])
        elif re.match('[0-9]+d[0-9]+$', command):
            parse_roll(command)
        elif command == 'chars':
            opt = print_chars()
        elif command == 'delchar':
            delete_character(args[0])
        elif command in ['clear','cls']:
            clear_screen()
        elif command in ['tracker', 't']:
            if not c:
                if get_decision('No current character, which is required to use trackers. Create a temporary character?'):
                    c = Char()
                else:
                    continue

            if args and args[0] in commands:
                print(f'Name {args[0]} is reserved.')
            elif len(args) == 1:
                c.trackers[args[0]] = Tracker(args[0])
            elif len(args) == 3 and args[1] == '=' and args[2].isnumeric():
                c.trackers[args[0]] = Tracker(args[0], default = int(args[2]))
            else:
                print('Usage: "tracker <name>" or "tracker <name> = <number>".')
        elif command in ['char','ch']:
            if args:
                try:
                    try:
                        if sb:
                            data = load_character(args[0].lower())
                            data.update({'sb':sb})
                            c = Char.from_json(data)
                        else:
                            c = Char.from_json(load_character(args[0].lower()))
                        print(f'Character loaded: {c.name}.')
                    except ValueError:
                        print(f'Ran into issue loading character {args[0]}.')
                except FileNotFoundError:
                    print(f'No character {args[0]} found.')
            else:
                if c:
                    print(f'Current character: {c.name}.')
                else:
                    c = Char.from_wizard()
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
                spell = ' '.join(args)
                if spell.isnumeric():
                    spell = Spell.from_json({
                        'name':f'a {level_prefix(int(spell))} Spell', 
                        'level': int(spell),
                        'school': 'placeholder'
                    })
                else:
                    spell=sb.get_spell(spell)
                
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
        elif c and command in c.trackers:
            if args:
                print(c.trackers[command].handle_command(args)) # Returns a string describing the operation undertaken
            else:
                print(c.trackers[command])
        else:
            print('Unknown command: ' + command)

    except Exception as e:
        print(f'Ran into a problem with that command: {e}')
