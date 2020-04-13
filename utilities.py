import os # Clear screen
import random # Roll dice
import difflib # Suggest similar commands
import constants

def printable_paragraph(string, width):
    if len(string) > width:
        out = ''
        line = ''
        word = ''
        for c in string:
            if len(line) + len(word) > width:
                out += '\n' + line.strip()
                line = ''

            if c == ' ':
                line += f' {word}'
                word = ''
            elif c == '\n':
                line += f' {word}'
                word = ''
                out += '\n' + line.strip()
                line = ''
            else:
                word += c

        out += '\n' + (line + ' ' + word).strip()
            
        return out
    else:
        return string

def level_prefix(level):
    if level == 0:
        return 'Cantrip'
    elif level == 1:
        return '1st Level'
    elif level == 2:
        return '2nd Level'
    elif level == 3:
        return '3rd Level'
    else:
        return f'{level}th Level'

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def parse_roll(string):
    qty, die = string.split('d')
    qty = int(qty) if len(qty) > 0 else 1
    die = int(die)

    rolls=[]
    for _ in range(0, qty):
        rolls.append(random.randint(1, die))

    if qty == 1:
        out = f'Roll: {rolls[0]}'
    else:
        out = 'Rolls: '
        for r in rolls:
            out += f'{str(r)}, '
        out = f'{out[:-2]}\tTotal: {sum(rolls)}'
    print(out)

    return (rolls, die) # for rerolling, etc

def reroll(rolls, die, rerolls):
    initial = sum(rolls)
    qty = len(rolls)
    
    for r in rerolls:
        rolls[r - 1] = random.randint(1, die)

    final = sum(rolls)

    change = f'({"+" if final >= initial else "-"}{abs(final - initial)})'

    if qty == 1:
        out = f'Roll: {rolls[0]} {change}'
    else:
        out = 'Rolls: '
        for r in rolls:
            out += f'{str(r)}, '
        out = f'{out[:-2]}\tTotal: {final} {change}'
    print(out)

    return (rolls, die)

# Parse a string like "school:evocation time:action"
def parse_spell_query(string):
    string += ' '

    queries = {}

    query_shortenings = {
        'n': 'name',
        's': 'school',
        'l': 'level',
        'c': 'cast',
        'r': 'rnge',
        'co': 'components',
        'd': 'duration',
        't': 'desc',
        'rit': 'ritual',
        'range': 'rnge'
    }

    quote = False
    colon = False
    query = ''
    criteria = ''
    for c in string:
        if c == ' ':
            if not quote and criteria:
                colon = False

                if query and criteria:
                    if query in query_shortenings:
                        query = query_shortenings[query]
                    queries[query.lower()] = criteria.lower()
                query = ''
                criteria = ''
            elif query in ['rit', 'ritual']:
                queries['ritual'] = 'true'
            elif colon and quote:
                criteria += c
        elif c == '"':
            if colon:
                quote = not quote
            else:
                raise ValueError
        elif c == ':' and not quote:
            colon = True
        else:
            if colon:
                criteria += c
            else:
                query += c

    return queries
        
def suggest_command(command):
    suggestion = difflib.get_close_matches(command, constants.commands, 1)
    if suggestion:
        suggestion = suggestion[0]
    return suggestion

def capitalise(string):
    words = string.split(' ')
    return ' '.join([w.capitalize() for w in words])
