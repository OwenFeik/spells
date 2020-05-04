import spellbook
import context
import dataloaders
import char

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
cfg = dataloaders.get_config()
c = None # Current player character

if cfg['load_previous_char'] and cache['character']:
    try:
        data = dataloaders.load_character(cache['character'])
        data.update({'sb': sb})
        c = char.Char.from_json(data)
        print(f'Character loaded: {str(c)}.')
    except FileNotFoundError:
        pass

context = context.Context(sb, cfg, c)

while True:
    context.get_input()
    context.handle_command()
