# Spells

## Intro

Spells is a command line utility for the management of DnD characters, under development. It is primarily targeted at allowing users to quickly and easily browse a library of spell descriptions, as well as keeping track of assorted values such as spells slots or hit points.

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
        "description": "Boom.",
        "ritual": false
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

As well as ```rit``` or ```ritual``` , which operates slightly differently in that no argument need be supplied, instead by inclusion of the search term, only spells which are rituals will be returned.

### Creating and Using a Character

Create a character using the ```char``` (or ```ch```) command, which will launch a simple wizard for you to create a character. This character can then be used for a variety of purposes, such as for keeping track of spells and other values.

The current character can be saved using the ```save``` command, and is automatically saved when the ```exit``` command is used (this can be avoided through the use of ```exit nosave``` if desired). When the app is started, it will open the character that was in use when it was closed, if possible.

A character can be loaded through ```ch <name>``` and a list of saved characters can be viewed through ```chars``` . These saved characters can be deleted through the use of the ```delchar``` command: ```delchar <name>``` will delete the saved character "name".

A new character can be started with ```newchar``` , which will replace the current character <b>without saving</b>.
Once one has a character, the following commands are available, in addition to the ability to track spell use and use trackers:

* ```levelup``` or ```level up``` : Add a level to the current character.
* ```slots``` : View currently available spell slots of each level.
* ```rest``` : Reset used spell slots, as well as any trackers configured to reset on rest.
* ```rename <name>``` : Change the name of the character to the supplied name.

### Using Trackers

Once you have created a character, you can use "trackers". These are simple numbers that are associated with a character and maintained through saving and loading. Trackers can be used for everything from hitpoints to magical item charges to the number of times Ragnar has fireballed an innocent civilian this session; the world is you oyster.

Start a tracker using ```t <name>``` or ```t <name> = <default value>``` and you'll have access to the following commands, accessed by using the format ```<name> <command>``` (for this reason, default command names cannot be used as tracker names). This first set of commands require no arguments:

* ```reset``` : Reset the tracker to its default value (0 unless set at creation or changed with the ```default``` command).
* ```rest``` : Toggle whether this tracker should be reset on a long rest (False by default).
* ```++``` : Increment the tracker by 1.
* ```--``` : Decrement the tracker by 1.

These commands all require an argument of ```<value>``` , the quantity applied to the tracker.

* ```<add or give or + or +=> <value>``` : Increase the trackers value by ```<value>``` .
* ```<subtract or take or - or -=> <value>``` : Reduce the trackers value by ```<value>``` .
* ```<set or => <value>```: Set the tracker to ```<value>``` .
* ```default <value>``` : Set the trackers default to ```<value>``` .

You can delete a tracker with ```deltracker <name>``` or ```dt <name>``` .

### Preparing and Casting Spells

Spells can be prepared using the command ```prep <spell name>``` (or just ```p``` ). This will toggle whether your character has them prepared. The list of prepared spells can be viewed with ```prepared``` (or ```prepped``` or ```pd``` ).

These spells can then be cast using ```cast <spell name>``` (or ```c``` ) , which will deduct a spell slot of the level of that spell. You can also cast spells of a certain level with ```cast <level>``` (e.g. ```c 5``` ), which can be useful if you are for example upcasting a spell and so want to use a slot of a higher level.

All spell slots are restored fully on a long rest (a use of the ```rest``` command). Your characters currently available spell slots can be viewed with ```slots``` .

### Rolling Dice

Dice can be rolled following the pattern of ```<n>d<size>``` like this, optionally prefaced by ```roll``` : 
* ```roll 8d6``` : roll 8d6
* ```d20``` : roll 1d20

If n is omitted, a value of 1 is assumed. 

Once you've rolled dice, you can use the ```reroll``` (or ```rr```) command to reroll them, such as for the Sorcerer "Empowered Spell" feature.

```
> 8d6
Rolls: 3, 3, 5, 6, 4, 6, 1, 6   Total: 34
> rr 1 2 7
Rolls: 5, 5, 5, 6, 4, 6, 6, 6   Total: 43 (+9)
```

### Other

* ```clear``` or ```cls``` will clear the screen.
