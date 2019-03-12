import os # Clear screen

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
