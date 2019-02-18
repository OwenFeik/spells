import json

from char import Char
from spellbook import Spellbook
from cli import print_spell,print_prepped,print_chars
from dataloaders import load_character,save_character
from utilities import clean_string

c=None # Current player character
try:
    sb=Spellbook() # Utility for retrieving spell information
except FileNotFoundError:
    print('Warning: No SpellBook available.')
opt=[] # Options which persist after certain functions

while True:
    
    try:
        inpt=[clean_string(string) for string in input('> ').split(' ') if string != '']
        command=inpt.pop(0)
        args=inpt
    except:
        command=''
        args=[]

    
    if command.isnumeric():
        if opt and int(command)<=len(opt)+1:
            if opt[0]=='spell':
                args=[opt[1][int(command)-1]]
                command='info'
            elif opt[0]=='char':
                args=[opt[1][int(command)-1]]
                command='char'
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
        spell=sb.get_spell(args[0])
        if spell:
            print_spell(spell)
        else:
            print('Sorry, I couldn\'t find that spell.')
    elif command=='prep' or command=='p':
        if c:
            spell=sb.get_spell(args[0])
            if spell:
                c.klasse.prepare_spell(spell)
            else:
                print('Sorry, I couldn\'t find that spell.')
        else:
            print('To prepare spells, start a character with "c <class>".')
    elif command=='prepped' or command=='prepared' or command=='pd':
        if c:
            opt=print_prepped(c,sb)
        else:
            print('To prepare spells, start a character with "c <class>".')
    elif command=='c' or command=='cast':
        if c:
            spell=sb.get_spell(args[0])
            if spell:
                c.cast_spell(spell)
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
    else:
        print('Sorry, I didn\'t understand that.')
