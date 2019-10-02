import os # Clear screen
from random import randint # Roll dice

def clean_string(string):
    while len(string)>0 and string[0]==' ':
        string=string[1:]
    while len(string)>0 and string[len(string)-1]==' ':
        string=string[:len(string)-1]
    return string

def printable_paragraph(string,width):
    if len(string)>width:
        out=''
        line=''
        word=''
        for c in string:
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
            
        return out
    else:
        return string

def level_prefix(level):
    if level==0:
        return 'Cantrip'
    elif level==1:
        return '1st Level'
    elif level==2:
        return '2nd Level'
    elif level==3:
        return '3rd Level'
    else:
        return f'{level}th Level'

def clear_screen():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system('clear')

def parse_roll(string):
    qty,die=(int(c) for c in string.split('d'))

    rolls=[]
    for _ in range(0,qty):
        rolls.append(randint(1,die))

    if qty==1:
        out=f'Roll: {rolls[0]}'
    else:
        out='Rolls: '
        for result in rolls:
            out+=f'{str(result)}, '
        out=f'{out[:-2]}\tTotal: {sum(rolls)}'
    print(out)


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
        'range': 'rnge'
    }

    quote = False
    colon = False
    query = ''
    criteria = ''
    for c in string:
        if c == ' ':
            if not quote:
                colon = False

                if query and criteria:
                    if query in query_shortenings:
                        query = query_shortenings[query]
                    queries[query.lower()] = criteria.lower()
                
                query = ''
                criteria = ''
            elif colon and quote:
                criteria += c
            else:
                raise ValueError
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

def parse_tracker_command(command):
    pass
