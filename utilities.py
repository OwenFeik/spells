def clean_string(string):
    while string[0]==' ':
        string=string[1:]
    while string[len(string)-1]==' ':
        string=string[:len(string)-1]
    return string
    