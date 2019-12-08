import re # Check command patterns
from char import Char
from tracker import Tracker
from spellbook import Spellbook, Spell
from cli import print_spell, print_prepped, print_chars, print_list, get_decision
from dataloaders import load_character, save_character, delete_character, get_cache, save_cache, clear_cache
from utilities import clear_screen, parse_roll, level_prefix, suggest_command, reroll
from constants import commands

cache = get_cache()
c = None # Current player character

if cache['character']:
    try:
        c = Char.from_json(load_character(cache['character']))
        print(f'Character loaded: {str(c)}.')
    except FileNotFoundError:
        pass

try:
    try:
        sb = Spellbook() # Utility for retrieving spell information
    except ValueError:
        print('Spellbook file corrupted. No Spellbook available.')
        sb = None
except FileNotFoundError:
    print('Warning: No Spellbook available.')
    sb = None

opt = [] # Options which persist after certain functions
roll = ([], None) # Dice previously rolled, for re-rolls

while True:
    
    try:
        inpt = [w.strip() for w in input('> ').lower().replace(',', '').split(' ') if w != '']
        command = inpt.pop(0)
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
            else:
                print('That option isn\'t available right now.')
        
        if command=='exit':
            if not args or not args[0] == 'nosave':
                if c:
                    save_character(c)
                    save_cache(c)
                else:
                    save_cache()
            else:
                clear_cache()
            raise SystemExit
        elif command in ['save']:
            if c:
                save_character(c)
                save_cache(c)
            else:
                print('No current character to save. Start one with "ch"!')
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
        elif re.match('^[0-9]*d[0-9]+$', command):
            roll = parse_roll(command)
        elif command in [ 'reroll', 'rr']:
            for i in range(len(args)):
                if args[i].isnumeric and int(args[i]) <= len(roll[0]):
                    args[i] = int(args[i])
                else:
                    print('Usage: "rr <dice> <to> <re> <roll>", where dice are identified by their index.')
                    break
            else:
                roll = reroll(roll[0], roll[1], args)
        elif command in ['characters', 'chars']:
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
                print(f'Name {args[0]} is a command and thus reserved.')
            elif len(args) == 1:
                c.trackers[args[0]] = Tracker(args[0])
            elif len(args) == 3 and args[1] == '=' and args[2].isnumeric():
                c.trackers[args[0]] = Tracker(args[0], default = int(args[2]))
            else:
                if c.trackers:
                    c.print_trackers()
                else:
                    print('Usage: "tracker <name>" or "tracker <name> = <number>".')
        elif command in ['char', 'ch', 'newchar']:
            if args and not command == 'newchar':
                try:
                    try:
                        if sb:
                            data = load_character(args[0].lower())
                            if sb:
                                data.update({'sb':sb})
                            c = Char.from_json(data)
                        else:
                            c = Char.from_json(load_character(args[0].lower()))
                        print(f'Character loaded: {str(c)}.')
                    except ValueError:
                        print(f'Ran into issue loading character {args[0]}.')
                except FileNotFoundError:
                    print(f'No character {args[0]} found.')
            else:
                if command == 'newchar' or not c:
                    c = Char.from_wizard()
                else:
                    print(f'Current character: {str(c)}.')
        elif command in ['prep','p']:
            if c:
                if not args:
                    print('Usage: "p <spell>".')
                    continue

                spell=sb.get_spell(' '.join(args))
                if spell:
                    c.prepare_spell(spell)
                else:
                    print('Sorry, I couldn\'t find that spell.')
            else:
                print('To prepare spells, start a character with "char".')
        elif command in ['prepped','prepared','pd']:
            if c:
                opt = print_prepped(c)
            else:
                print('To prepare spells, start a character with "char".')
        elif command in ['cast','c']:
            if c:
                if not args:
                    print('Usage: "c <spell>" or "c <level>".')
                    continue

                spell = ' '.join(args)
                if spell.isnumeric():
                    spell = Spell.from_json({
                        'name':f'a {level_prefix(int(spell))} Spell', 
                        'level': int(spell),
                        'school': 'placeholder'
                    })
                else:
                    spell = sb.get_spell(spell)
                
                if spell:
                    c.cast_spell(spell)
                else:
                    print(f'No spell {args[0]} found.')
            else:
                print('To cast spells, start a character with "char".')
        elif command=='slots':
            if c:
                c.print_spell_slots()
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
                c.level_up()
        elif c and command in c.trackers:
            if args:
                print(c.trackers[command].handle_command(args)) # Returns a string describing the operation undertaken
            else:
                print(c.trackers[command])
        else:
            if command:
                suggestion = suggest_command(command)
                if suggestion:
                    print(f'Unknown command: {command}. Perhaps you meant "{suggestion}".')
                else:
                    print(f'Unknown command: {command}.')

    except Exception as e:
        print(f'Ran into a problem with that command: {e}')
