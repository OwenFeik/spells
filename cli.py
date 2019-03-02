from os import get_terminal_size

from dataloaders import current_chars
from utilities import clean_string

def print_spell(spell):
    width=get_terminal_size()[0]
    if width<60:
        pass
    elif width<120:
        width=int(0.8*width)
    else:
        width=int(0.6*width)

    out=''

    if len(spell.name)+len(spell.school)<width:
        out=f'\n{spell.name} | {spell.school}'
    else:
        out=f'\n{spell.name}\n{spell.school}'

    if len(spell.cast)+len(spell.rnge)<width:
        out+=f'\n{spell.cast} | {spell.rnge}'
    else:
        out+=f'\n{spell.cast}\n{spell.rnge}'
    
    if len(spell.components)+len(spell.duration)<width:
        out+=f'\n{spell.components} | {spell.duration}'
    else:
        out+=f'\n{spell.components}\n{spell.duration}'

    if len(spell.desc)>width:
        out+='\n'
        desc=spell.desc

        line=''
        word=''
        for c in desc:
            if len(line)+len(word)>width:
                out+='\n'+clean_string(line)
                line=''

            if c==' ':
                line+=f' {word}'
                word=''
            elif c=='\n':
                line+=f' {word}'
                word=''
                out+='\n'+clean_string(line)
                line=''
            else:
                word+=c

        out+='\n'+clean_string(line+' '+word)
    else:
        out+=f'\n\n{spell.desc}\n'

    out+='\n'
    print(out)

def print_prepped(char,spellbook):
    prepared=spellbook.get_spells(char.klasse.prepared)
    cantrips=spellbook.get_spells(char.klasse.cantrips)
    prepped='\nPrepared:\n'
    for i in range(0,len(prepared)):
        prepped+=f'\n[{i+1}] {prepared[i].name} | {prepared[i].school}'
    prepped+='\n\nCantrips:\n'
    for i in range(0,len(cantrips)):
        prepped+=f'\n[{i+1+len(prepared)}] {cantrips[i].name} | {cantrips[i].school}'
    prepped=prepped[1:]
    print(f"\n{char.name}:\n{prepped}\n")
    opt=[spell.name for spell in prepared]+[spell.name for spell in cantrips]
    return ('spell',opt)

def print_chars():
    chars=current_chars()
    char_string=''
    for i in range(len(chars)):
        char_string+=f"\n[{i+1}] {chars[i].get('name')} | {chars[i].get('class').get('class')} {chars[i].get('class').get('level')}"
    print(f'\nCharacters:\n{char_string}\n')
    opt=[char.get('name').lower() for char in chars]
    return ('char',opt)
