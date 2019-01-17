import re
import json

from char import Char
from spell import Spellbook
from cli import print_spell,print_prepped

sb=Spellbook()
c=Char()

while True:
    
    try:
        inpt=input('> ')
        command=re.search('[a-z]+ ?',inpt).group(0)
        inpt=inpt[len(command):]
        if command[len(command)-1]==' ':
            command=command[:len(command)-1]
        arg=inpt
    except:
        print("Sorry, I didn't understand that.")

    if command=='exit':
        with open(f'{c.name}.json','w') as f:
            json.dump(c.to_json(),f,indent=4)
        exit()
    elif command=='char' or command=='c':
        if arg:
            try:
                with open(f'{arg}.json','r') as f:
                    c=Char.from_json(json.load(f))
            except FileNotFoundError:
                c=Char(arg)
        else:
            print("Which character?")
    elif command=='info' or command=='i':
        spell=sb.get_spell(arg)
        if spell:
            print_spell(spell)
        else:
            print('Sorry, I couldn\'t find that spell.')
    elif command=='prep' or command=='p':
        spell=sb.get_spell(arg)
        if spell:
            c.prepare_spell(spell)
        else:
            print('Sorry, I couldn\'t find that spell.')
    elif command=='prepped':
        print_prepped(c)
    elif command=='rename':
        c.name=arg
    