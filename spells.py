import re # Check command patterns
import char
import tracker
import spellbook
import cli
import dataloaders
import utilities
import constants

try:
    try:
        sb = spellbook.Spellbook() # Utility for retrieving spell information
    except ValueError:
        print('Spellbook file corrupted. No Spellbook available.')
        sb = None
except FileNotFoundError:
    print('Warning: No Spellbook available.')
    sb = None

cache = dataloaders.get_cache()
c = None # Current player character

if cache['character']:
    try:
        data = dataloaders.load_character(cache['character'])
        data.update({'sb': sb})
        c = char.Char.from_json(data)
        print(f'Character loaded: {str(c)}.')
    except FileNotFoundError:
        pass

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
                elif opt[0] == 'roll':
                    command = opt[1][index]
                    args = []
            else:
                print('That option isn\'t available right now.')
                continue
        
        if command=='exit':
            if not args or not args[0] == 'nosave':
                if c:
                    dataloaders.save_character(c)
                    dataloaders.save_cache(c)
                else:
                    dataloaders.save_cache()
            else:
                dataloaders.clear_cache()
            raise SystemExit
        elif command in ['save']:
            if c:
                dataloaders.save_character(c)
                dataloaders.save_cache(c)
            else:
                print('No current character to save. Start one with "ch"!')
        elif command in ['info', 'i']:
            arg = ' '.join(args)
            spell = sb.get_spell(arg)
            if spell:
                opt = cli.print_spell(spell)
            else:
                print('Sorry, I couldn\'t find that spell.')
        elif command in ['search', 's']:
            spells = sb.handle_query(' '.join(args))
            if spells:
                if len(spells) == 1:
                    opt = cli.print_spell(spells[0])
                else:
                    spell_names = [spell.name for spell in spells]
                    cli.print_list('Results', spell_names)
                    opt = ['spell', spell_names]
            else:
                print('Couldn\'t find any spells matching that description.')
        elif command == 'roll':
            utilities.parse_roll(args[0])
        elif re.match('^[0-9]*d[0-9]+$', command):
            roll = utilities.parse_roll(command)
        elif command in [ 'reroll', 'rr']:
            for i in range(len(args)):
                if args[i].isnumeric and int(args[i]) <= len(roll[0]):
                    args[i] = int(args[i])
                else:
                    print('Usage: "rr <dice> <to> <re> <roll>", where dice are identified by their index.')
                    break
            else:
                roll = utilities.reroll(roll[0], roll[1], args)
        elif command in ['characters', 'chars']:
            opt = cli.print_chars()
        elif command == 'delchar':
            dataloaders.delete_character(' '.join(args))
        elif command in ['clear','cls']:
            utilities.clear_screen()
        elif command in ['tracker', 't']:
            if not c:
                if cli.get_decision('No current character, which is required to use trackers. Create a temporary character?'):
                    c = char.Char()
                else:
                    continue

            if args and args[0] in constants.commands:
                print(f'Name {args[0]} is a command and thus reserved.')
            elif len(args) == 1:
                c.trackers[args[0]] = tracker.Tracker(args[0])
            elif len(args) == 3 and args[1] == '=' and args[2].isnumeric():
                c.trackers[args[0]] = tracker.Tracker(args[0], default = int(args[2]))
            else:
                if c.trackers:
                    c.print_trackers()
                else:
                    print('Usage: "tracker <name>" or "tracker <name> = <number>".')
        elif command in ['deltracker', 'dt']:
            if not c:
                print('No current character, cannot delete tracker.')
                continue

            try:
                del c.trackers[args[0]]
                print(f'Tracker {args[0]} deleted.')
            except KeyError:
                print(f'Tracker {args[0]} does not exist.')
        elif command in ['char', 'ch', 'newchar']:
            if args and not command == 'newchar':
                try:
                    try:
                        if sb:
                            data = dataloaders.load_character(args[0].lower())
                            if sb:
                                data.update({'sb':sb})
                            c = char.Char.from_json(data)
                        else:
                            c = char.Char.from_json(dataloaders.load_character(args[0].lower()))
                        print(f'Character loaded: {str(c)}.')
                    except ValueError:
                        print(f'Ran into issue loading character {args[0]}.')
                except FileNotFoundError:
                    print(f'No character {args[0]} found.')
            else:
                if command == 'newchar' or not c:
                    c = char.Char.from_wizard()
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
                opt = cli.print_prepped(c)
            else:
                print('To prepare spells, start a character with "char".')
        elif command in ['cast','c']:
            if c:
                if not args:
                    print('Usage: "c <spell>" or "c <level>".')
                    continue

                spell = ' '.join(args)
                if spell.isnumeric():
                    spell = spellbook.Spell.from_json({
                        'name':f'a {utilities.level_prefix(int(spell))} Spell', 
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
            if not args:
                print('Usage: "rename <new name>"')
            elif not c:
                print('No current character to rename. Start or load one with "char".')
            else:            
                old_name = c.name
                c.name = ' '.join(args)
                print(f'Renamed {utilities.capitalise(old_name)} to {utilities.capitalise(c.name)}.')
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
                suggestion = utilities.suggest_command(command)
                if suggestion:
                    print(f'Unknown command: {command}. Perhaps you meant "{suggestion}".')
                else:
                    print(f'Unknown command: {command}.')

    except Exception as e:
        print(f'Ran into a problem with that command: {e}')
