from os import get_terminal_size

from dataloaders import current_chars
from utilities import clean_string,printable_paragraph

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
    elif spell.level==1:
        school='1st Level '+spell.school
    elif spell.level==2:
        school='2nd Level '+spell.school
    elif spell.level==3:
        school='3rd Level '+spell.school
    else:
        school=f'{spell.level}th Level {spell.school}'

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
        out+=f'{components}\n{duration}'

    out+=f'\n{printable_paragraph(spell.desc,width)}\n'

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
