from char import Char
from spellbook import Spellbook
from cli import print_spell,print_prepped,print_chars
from dataloaders import load_character,save_character,delete_character
from utilities import clean_string

c=None # Current player character

try:
    try:
        sb=Spellbook() # Utility for retrieving spell information
    except ValueError:
        print('Spellbook file corrupted. No Spellbook available.')
except FileNotFoundError:
    print('Warning: No Spellbook available.')

opt=[] # Options which persist after certain functions

while True:
    
    try:
        inpt=[clean_string(string) for string in input('> ').split(' ') if string != '']
        command=inpt.pop(0)
        args=inpt
    except:
        command=''
        args=[]

    try:
        if command.isnumeric():
            if opt and int(command)<len(opt[1])+1:
                if opt[0]=='spell':
                    args=[opt[1][int(command)-1]]
                    command='info'
                elif opt[0]=='char':
                    args=[opt[1][int(command)-1]]
                    command='char'
                elif opt[0]=='class':
                    if opt[2]=='cast':
                        c.cast_spell(sb.get_spell(opt[3]),opt[1][int(command)-1])
                    elif opt[2]=='prep':
                        c.prepare_spell(sb.get_spell(opt[3]),opt[1][int(command)-1])
            else:
                print('That option isn\'t available right now.')
        
        if command=='exit':
            if c:
                save_character(c)
            raise SystemExit
        elif command=='char' or command=='ch':
            if args:
                try:
                    try:
                        if sb:
                            data=load_character(args[0].lower())
                            data.update({'sb':sb})
                            c=Char.from_json(data)
                        else:
                            c=Char.from_json(load_character(args[0].lower()))
                        print(f'Character loaded: {args[0]}.')
                    except ValueError:
                        print(f'Ran into issue loading character {args[0]}.')
                except FileNotFoundError:
                    try:
                        c=Char(**{'class':args[0]})
                        print(f'Temp character of class {args[0]} created. Use "rename <name>" for a new name.')
                    except ValueError:
                        print(f'No class {args[0]} found.')
            else:
                if c:
                    print(f'Current character: {c.name}.')
                else:
                    c=Char.from_wizard()
        elif command=='info' or command=='i':
            arg=' '.join(args)
            spell=sb.get_spell(arg)
            if spell:
                print_spell(spell)
            else:
                print('Sorry, I couldn\'t find that spell.')
        elif command=='prep' or command=='p':
            if c:
                spell=sb.get_spell(' '.join(args))
                if spell:
                    opt=c.prepare_spell(spell)
                else:
                    print('Sorry, I couldn\'t find that spell.')
            else:
                print('To prepare spells, start a character with "c <class>".')
        elif command=='prepped' or command=='prepared' or command=='pd':
            if c:
                opt=print_prepped(c)
            else:
                print('To prepare spells, start a character with "c <class>".')
        elif command=='cast' or command=='c':
            if c:
                spell=sb.get_spell(' '.join(args))
                if spell:
                        opt=c.cast_spell(spell)
                else:
                    print(f'No spell {args[0]} found.')
            else:
                print('To cast spells, start a character with "char <class>".')
        elif command=='rename':
            c.name=args[0]
        elif command=='rest':
            if c:
                c.long_rest()
            else:
                print('To rest, start or load a character with "c <class>".')
        elif command=='chars':
            opt=print_chars()
        elif command=='delchar':
            delete_character(args[0])
    except Exception as e:
        print(f'Ran into a problem with that command: {e}')
