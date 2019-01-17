import requests
import json
import re
from bs4 import BeautifulSoup
import asyncio
from spell import Spell

def clean_string(string):
    while string!='' and string[0]==' ':
        string=string[1:]
    while string!='' and string[len(string)-1]==' ':
        string=string[0:len(string)-1]
    return string

async def make_spell(spell):
    data=requests.get('https://5thsrd.org/spellcasting/spells/'+spell).text
    
    sp=BeautifulSoup(data,'lxml')
    data=sp.find('div',{'role':'main'}).text.split('\n')

    name=clean_string(data[0])
    levl=clean_string(data[1])
    cast=clean_string(data[2])
    rnge=clean_string(data[3])
    cmpn=clean_string(data[4])
    durn=clean_string(data[5])
    desc=clean_string('\n'.join(data[6:]))

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