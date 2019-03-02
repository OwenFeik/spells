def clean_string(string):
    while len(string)>0 and string[0]==' ':
        string=string[1:]
    while len(string)>0 and string[len(string)-1]==' ':
        string=string[:len(string)-1]
    return string
