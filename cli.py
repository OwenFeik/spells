
def print_spell(spell):
    print(f'\n{spell.name} | {spell.levl}\n{spell.cast} | {spell.rnge}\n{spell.cmpn} | {spell.durn}\n\n{spell.desc}\n')

def print_prepped(char):
    prepped='\n'.join(char.prepared)
    print(f"\n{char.name}:\n\n{prepped}\n")
