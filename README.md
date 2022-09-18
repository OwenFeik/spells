# Spells

## Intro

Spells is a python 3 command line utility for the management of DnD characters,
under development. It is primarily targeted at allowing users to quickly and
easily browse a library of spell descriptions, as well as keeping track of
assorted values such as spells slots or hit points. It aims to be easy to learn
and quick to use.

### Install

`
git clone https://github.com/OwenFeik/spells.git
cd spells
python3 spells.py
`

## Usage

### Resources

The resources folder (`./resources/`) should contain `spells.json`: a JSON file
containing a list of spells of the following format.

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
        "ritual": false,
        "classes": [ "Wizard" ],
        "subclasses": [ "Druid (Circle of Elements (Fire))" ],
        "alt_names": [ "big boom", "'splosion" ]
    }
```

An example file is included, though the user is free to extend or replace this
by editing or replacing the file.

### Searching for Spells

Spells in the spells.json file can be searched from the app through the
following commands:

* `<i or info> <spell name>` : The spells information block, if the spell is
found.
* `<s or search> <arguments>` : A list of spells meeting the specified
requirements.

Arguments for `search` should be formatted like so:
`n: Fireball co: "bat guano"` or `t: "wisdom saving throw" l: 4` . The
following search categories are available:
* `n` or `name` , then name of the spell.
* `s` or `school` , the school of magic.
* `l` or `level` , the spell's level.
* `c` or `cast` , casting time.
* `r` or `range` , the spell's range.
* `co` or `components` , components of the spell.
* `d` or `duration` , the spell's duration.
* `t` or `desc` , the description text.
* `cl` or `classes` , classes which have access to the spell.
* `sc` or `subclasses`, subclasses which have access to the spell.

As well as `rit` or `ritual` , which operates slightly differently in
that no argument need be supplied, instead by inclusion of the search term, only
spells which are rituals will be returned.

When using these functions, as well as some others, you may see lists or
footnotes with numbers encased in square brackets like so: `[1]` . These
indicate "options"; until you use another command which generates options, you
can use the options from this command by entering the corresponding number. This
includes things like selecting search results, or performing dice rolls
prescribed by spells.

### Creating and Using a Character

Create a character using the `char` (or `ch`) command, which will launch
a simple wizard for you to create a character. This character can then be used
for a variety of purposes, such as for keeping track of spells and other values.

The current character can be saved using the `save` command, and is
automatically saved when the `exit` command is used (this can be avoided
through the use of `exit nosave` if desired). When the app is started, it
will open the character that was in use when it was closed, if possible.

A character can be loaded through `ch <name>` and a list of saved characters
can be viewed through `chars` . These saved characters can be deleted
through the use of the `delchar` command: `delchar <name>` will delete
the saved character "name". A save file located outside of the saves folder can
be loaded through the use of `load <file>` command.

A new character can be started with `newchar` , which will replace the
current character <b>without saving</b>.
Once one has a character, the following commands are available, in addition to
the ability to track spell use and use trackers:

* `levelup` or `level up` : Add a level to the current character.
* `slots` : View currently available spell slots of each level.
* `rest` : Reset used spell slots, as well as any trackers configured to
reset on rest.
* `rename <name>` : Change the name of the character to the supplied name.
* `stats` : Add stats to the character, or view the character's stats. Use
`stats update` to update the value of a stat.
* `note` : Take a note that is saved with the character.
* `notes` : View, edit or delete previously taken notes for this character.

### Skills

Spells can track your skill proficiencies and perform skill checks for you. To
manage your proficiencies, use the following commands

* `profs` or `proficiences` : View existing proficiency entries for all
    skills
* `prof <skill>` or `proficiency <skill>` : Toggle proficiency in `<skill>` .
* `exp <skill>` or `expertise <skill>` : Toggle expertise in `<skill>` .
* `sc <skill>` or `skillcheck <skill>` : Perform a skill check for `<skill>`,
    using your characters stats, level and configured proficiency information.

For all of these commands, `<skill>` may be a unique prefix of a skill name or
a configured shortcut name as detailed below. The following comands deal with
customising the skill list.

* `newskill <name>` : Create a new skill named `<name>` . You will be prompted
    to configure the correct statistic and can then manage proficiency as
    normal.
* `skillalt <skill>` : Add a shortcut name for `<skill>` .
* `delskill <skill>` : Delete a skill from the list.

A few intuitive `<skill>` shortcut names are included by default, but if these
are undesired they can be removed by deleting and recreating the relevant
skills. 

### Using Trackers

Once you have created a character, you can use "trackers". These are simple
numbers that are associated with a character and maintained through saving and
loading. Trackers can be used for everything from hitpoints to magical item
charges to the number of times Ragnar has fireballed an innocent civilian this
session; the world is you oyster.

Start a tracker using `t <name>` or `t <name> = <default value>` and
you'll have access to the following commands, accessed by using the format
`<name> <command>` (for this reason, default command names cannot be used
as tracker names). This first set of commands require no arguments:

* `reset` : Reset the tracker to its default value (0 unless set at creation
or changed with the `default` command).
* `rest` : Toggle whether this tracker should be reset on a long rest (False
by default).
* `++` : Increment the tracker by 1.
* `--` : Decrement the tracker by 1.
* `default` : With no argument, prints the current default.

These commands all require an argument of `<value>` , the quantity applied
to the tracker. `<value>` can be either an integer or a dice roll formatted
like `1d8` or `2d10` . If a dice roll is supplied, the value will be
rolled and then applied.

* `<add or give or + or +=> <value>` : Increase the trackers value by
`<value>` .
* `<subtract or take or - or -=> <value>` : Reduce the trackers value by
`<value>` .
* `<set or => <value>` : Set the tracker to `<value>` .
* `default <value>` : Set the trackers default to `<value>` .

You can delete a tracker with `deltracker <name>` or `dt <name>` .

### Tracker Collections

Trackers can be organised into tracker collections. These are created with the
command `tc <name>` which will create a collection with the name
`<name>` . Trackers can be added to this collection with
`<name> add <tracker>` where `<name>` is the name of the collection and
`<tracker>` is the name of the tracker to create. These can then be removed
with `<name> remove <tracker>` .

Trackers held in a collection can be accessed through
`<collection>.<tracker>` and interacted with as normal trackers. One can
create a tracker in a collection with `t <collection>.<tracker>` .

A preset exists for tracking coins. The command `tc coins` (or
`tc wealth`) will prompt the creation of a special kind of tracker that has
facilities for conversion between denominations of coins in Dungeons and
Dragons. This collection offers interpretation for the following commands.

* `coins add <qty> <denomination>`
* `coins spend <qty><denomination>`

Where `<qty>` is an integer and `<denomination>` is one of `pp` , 
`gp` , `sp` , `cp` . This will either add this many coins to the
relevant denomination tracker or deduct this many coins, using other
denominations if exact change is impossible.

Optionally one can also enable electrum pieces, `ep` , with
`coins enable_electrum` or `coins enable ep` . These can be disabled
later with `coins disable_electrum` or `coins disable ep` .

### Preparing and Casting Spells

Spells can be prepared using the command `prep <spell name>` (or just
`p` ). This will toggle whether your character has them prepared. The list
of prepared spells can be viewed with `prepared` (or `prepped` or
`pd` ).

These spells can then be cast using `cast <spell name>` (or `c` ) ,
which will deduct a spell slot of the level of that spell. You can also cast
spells of a certain level with `cast <level>` (e.g. `c 5` ), which can
be useful if you are for example upcasting a spell and so want to use a slot of
a higher level.

All spell slots are restored fully on a long rest (a use of the `rest`
command). Your characters currently available spell slots can be viewed with
`slots` .

### Rolling Dice

Dice can be rolled following the pattern of `<n>d<size>`, optionally
prefaced by `roll`. If the first term in your roll is an integer, it will be
necessary to prefix as it will be assumed you are attempting to accesss an
option.
* `roll 8d6` : roll 8d6
* `d20` : roll 1d20

If n is omitted, a value of 1 is assumed. A variety of more advanced syntax
options for rolling are available. The specification followed is:
`
<const> <operation> <n>d<size><advstr> <mods> k<keep>
`
Where

* `const` is an integer
* `operation` is the arithmetic operation used to apply `const` to the
result of the roll
* `n` is the number of dice to roll
* `size` is the number of faces on these dice
* `advstr` is any number of "a"s and "d"s to determine whether the roll is
at advantage or disadvantage.
* `mods` is any number of terms of the form `<operation> <value>` e.g.
`+ 3` or `* 2`
* `keep` is the number of die to add to form the result e.g. `k3` to
return the sum of the two highest rolls as the result.

Some examples:

```
> roll 6 4d6k3
4d6 keep 3      Rolls: 2, 6, 4, 2       Total: 12
4d6 keep 3      Rolls: 4, 3, 2, 3       Total: 10
4d6 keep 3      Rolls: 4, 1, 5, 3       Total: 12
4d6 keep 3      Rolls: 5, 6, 2, 4       Total: 15
4d6 keep 3      Rolls: 3, 2, 5, 6       Total: 14
4d6 keep 3      Rolls: 1, 1, 1, 6       Total: 8
Grand Total: 71
> d20a + 3
d20a + 3        Rolls: 16, 4    Total: 19
> roll 2 * 2d10
2d10 * 2        Rolls: 5, 5     Total: 20
```

Once you've rolled dice, you can use the `reroll` (or `rr`) command to
reroll them, such as for the Sorcerer "Empowered Spell" feature.

```
> 8d6
Rolls: 3, 3, 5, 6, 4, 6, 1, 6   Total: 34
> rr 3
Rolls: 5, 5, 5, 6, 4, 6, 6, 6   Total: 43 (+9)
```

The format to reroll is `rr <n>` where `n` is the number of die to reroll.

If you have an active character when rolling dice, the roll results are stored
alongside that character, to enable the following `stats` commands.

* `roll stats` which will print out the average results for each of the common
    RPG dice.
* `roll stats <period>` where `<period>` is one of `day`, `week`, `month` or
    `year`, which will do the same but limiting to rolls from the past day,
    week, etc.
* `roll stats clear` will clear all stored stats.

### Other

* `clear` or `cls` will clear the screen.
* `settings` will allow you to change some behaviours.

Two commands are available which use `git` to check for updates to the app.

* `update` downloads a new version. 
* `update_check` or `update check` checks if a new version is available.

A third command `update_spells` (or `update spells`) updates the apps
spell list by downloading the default list again.
