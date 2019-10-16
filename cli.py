from os import get_terminal_size

from dataloaders import current_chars
from utilities import printable_paragraph, level_prefix

def print_spell(spell):
    width=get_terminal_size()[0]
    if width<60:
        pass
    elif width<120:
        width=int(0.8*width)
    else:
        width=int(0.6*width)

    out=''

    if spell.level==0:
        school=spell.school+' Cantrip'
    else:
        school=f'{level_prefix(spell.level)} {spell.school}'

    if len(spell.name)+len(school)<width:
        out=f'\n{spell.name} | {school}'
    else:
        out=f'\n{spell.name}\n{school}'

    if len(spell.cast)+len(spell.rnge)+24<width:
        out+=f'\nCasting Time: {spell.cast} | Range: {spell.rnge}'
    else:
        out+=f'\nCasting Time: {spell.cast}\nRange: {spell.rnge}'
    
    if len(spell.components)+len(spell.duration)+25<width:
        out+=f'\nComponents: {spell.components} | Duration: {spell.duration}'
    else:
        components=printable_paragraph('Components: '+spell.components,width)
        duration=printable_paragraph('Duration: '+spell.duration,width)
        out+=f'\n{components}\n{duration}'

    out+=f'\n{printable_paragraph(spell.desc,width)}\n'

    print(out)

def print_prepped(char):
    out=''
    opt=[]
    for klasse in [klasse for klasse in char.klasses if hasattr(klasse,'spells')]:
        out+=f'\n\n{klasse.klasse.capitalize()}:\n'
        spells={i:[] for i in range(0,10)}
        if klasse.spells:
            for spell in sorted(klasse.spells,key=lambda k:k.name):
                spells[spell.level].append(spell.name)
            for i in range(0,10):
                if spells[i]:
                    out+=f'\n\t{level_prefix(i)}:'
                    for spell in spells[i]:
                        opt.append(spell)
                        out+=f'\n\t\t[{len(opt)}] {spell}'
        else:
            out+='\tNo spells.'

    print(out[1:]+'\n')
    return ('spell',opt)

def print_chars():
    chars=current_chars()
    if chars:
        char_string=''
        for i in range(len(chars)):
            char_string+=f"\n[{i+1}] {chars[i].get('name')} | "
            first=True
            for klasse in chars[i].get('classes'):
                if not first:
                    char_string+=', '
                char_string+=f"{klasse.get('class').capitalize()} {klasse.get('level')}"
                first=False
        print(f'\nCharacters:\n{char_string}\n')
        opt=[char.get('name').lower() for char in chars]
        return ('char',opt)
    else:
        print('No characters saved.')

def print_list(title, items):
    print(f'\n{title}:\n')
    
    count = 0
    for item in items:
        count += 1
        print(f'\t[{count}] {item}')
    print('\n')

def get_input(prompt):
    return [string for string in input(f'{prompt}> ').strip().split(' ') if string != ''] 

def get_decision(prompt):
    return input(f'{prompt} (y/n) > ').strip().lower() in ['y', '']

def get_choice(prompt, items):
    print_list(prompt, items)

    choice = input('> ')
    while not choice.isnumeric() and not choice in items:
        choice = input('Please enter the number of an item from the options > ')
    
    if choice.isnumeric():
        return items[int(choice) - 1]
    elif choice in items:
        return choice
        