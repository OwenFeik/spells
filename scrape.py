import requests
import re
import json
import asyncio
from spell import Spell

def clean_start(string):
    while '>' in string:
        string=string[string.find('>')+1:]
    while string!='' and string[0]==' ':
        string=string[1:]
    while string!='' and string[len(string)-1]==' ':
        string=string[0:len(string)-1]
    return string

def clean_name(string):
    return string[:len(string)-18]

def remove_html(string):
    string=string.replace('<br />','').replace('<strong>','').replace('</strong>','').replace('<em>','').replace('</em>','')
    return string.replace('</p>\n<ul>\n<li>','\n- ').replace('</li>\n<li>','\n- ').replace('</li>\n</ul></div>\n        ','</p>')

async def make_spell(spell):
    data=requests.get('https://5thsrd.org/spellcasting/spells/'+spell).text
    
    name=clean_name(clean_start(re.search('<title>[^<]+',data).group(0)))
    levl=clean_start(re.search('<p> ?<em>[^<]+',data).group(0))
    cast=clean_start(re.search('Casting Time:</strong> ?[^<]+',data).group(0))
    rnge=clean_start(re.search('Range:?</strong>:?[^<]+',data).group(0))
    cmpn=clean_start(re.search('Components:?</strong>:?[^<]+',data).group(0))
    durn=clean_start(re.search('Duration:?</strong>:?[^<]+',data).group(0))
    try:
        desc=re.search('<p>[^<]+</p></div>',remove_html(data)).group(0)
        desc=clean_start(desc[:len(desc)-10])
    except:
        desc=''

    spl=Spell(name,levl,cast,rnge,cmpn,durn,desc)
    return spl.to_json()

async def make_spells(urllist):
    out=[]
    for spell in urllist:
        out.append(await make_spell(spell))
    return out

data=requests.get('https://5thsrd.org/spellcasting/spell_lists/cleric_spells/').text
spells=re.findall('../../../spellcasting/spells/[a-zA-Z_]+',data)
spells=[spell[29:] for spell in spells]

loop=asyncio.get_event_loop()
out=loop.run_until_complete(make_spells(spells))

spell_data={i:[] for i in range(0,10)}
for item in out:
    if 'cantrip' in item['level']:
        spell_data[0].append(item)
    elif '1st' in item['level']:
        spell_data[1].append(item)
    elif '2nd' in item['level']:
        spell_data[2].append(item)
    elif '3rd' in item['level']:
        spell_data[3].append(item)
    elif '4th' in item['level']:
        spell_data[4].append(item)
    elif '5th' in item['level']:
        spell_data[5].append(item)
    elif '6th' in item['level']:
        spell_data[6].append(item)
    elif '7th' in item['level']:
        spell_data[7].append(item)
    elif '8th' in item['level']:
        spell_data[8].append(item)
    elif '9th' in item['level']:
        spell_data[9].append(item)

with open('spells.json','w') as f:
    json.dump(spell_data,f,indent=4)