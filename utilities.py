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
