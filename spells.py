import re
import json

from char import Char
from spellbook import Spellbook
from cli import print_spell,print_prepped,print_chars
from dataloaders import load_character

c=None
sb=Spellbook('cleric')
opt=[]

while True:
    
    try:
        inpt=input('> ')
        command=re.search('[a-z0-9]+ ?',inpt).group(0)
        inpt=inpt[len(command):]
        while command[len(command)-1]==' ':
            command=command[:len(command)-1]
        arg=inpt
    except:
        command=''
        arg=''

    
    if command.isnumeric():
        if opt and int(command)<=len(opt)+1:
            if opt[0]=='spell':
                print_spell(sb.get_spell(opt[1][int(command)-1]))
            elif opt[0]=='char':
                arg=opt[1][int(command)-1]
                command='char'
        else:
            print('That option isn\'t available right now.')
    
    if command=='exit':
        with open(f'saves/{c.name.lower()}.json','w') as f:
            json.dump(c.to_json(),f,indent=4)
        raise SystemExit
    elif command=='char' or command=='ch':
        if arg:
            try:
                c=Char.from_json(load_character(arg.lower()))
                print(f'Character loaded: {arg}.')
            except FileNotFoundError:
                try:
                    c=Char(arg)
                    print(f'Temp character of class {arg} created. Use "rename <name>" for a new name.')
                except ValueError:
                    print(f'No class {arg} found.')
        else:
            if c:
                print(f'Current character: {c.name}.')
            else:
                print('No current character.')
    elif command=='info' or command=='i':
        spell=sb.get_spell(arg)
        if spell:
            print_spell(spell)
        else:
            print('Sorry, I couldn\'t find that spell.')
    elif command=='prep' or command=='p':
        if c:
            spell=sb.get_spell(arg)
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
            spell=sb.get_spell(arg)
            if spell:
                c.klasse.cast_spell(spell)
            else:
                print(f'No spell {arg} found.')
        else:
            print('To cast spells, start a character with "char <class>".')
    elif command=='rename':
        c.name=arg
    elif command=='rest':
        if c:
            c.klasse.long_rest()
        else:
            print('To rest, start or load a character with "c <class>".')
    elif command=='chars':
        opt=print_chars()
    else:
        print('Sorry, I didn\'t understand that.')
