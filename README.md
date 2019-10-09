# Spells

## Intro

Spells is a command line utility for the management of DnD characters, under development. It is primarily targeted at allowing users to quickly and easily utilise

## Quick Start

### Resources:

The resources folder ("./resources/") should contain "spells.json": a JSON file containing a list of spells of the following format.

```json 
    {
        "name": "Fireball",
        "school": "Evocation",
        "level": 3,
        "cast": "1 action",
        "range": "150 feet",
        "components": "V S M: A tiny ball of bat guano and sulfur",
        "duration": "Instantaneous",
        "description": "Boom."
    }
```
### Searching for Spells

Spells in the spells.json file can be searched from the app through the following commands:

* ```<i or info> <spell name>``` : The spells information block, if the spell is found.
* ```<s or search> <arguments>``` : A list of spells meeting the specified requirements.

Arguments for ```search``` should be formatted like so: ```n: Fireball co: "bat guano"``` or ```t: "wisdom saving throw" l: 4``` . The following search categories are available:
* ```n``` or ```name``` , then name of the spell.
* ```s``` or ```school``` , the school of magic.
* ```l``` or ```level``` , the spell's level.
* ```c``` or ```cast``` , casting time.
* ```r``` or ```range``` , the spell's range.
* ```co``` or ```components``` , components of the spell.
* ```d``` or ```duration``` , the spell's duration.
* ```t``` or ```desc``` , the description text.
