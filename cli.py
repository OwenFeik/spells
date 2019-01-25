from dataloaders import current_chars

def print_spell(spell):
    print(str(spell))

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