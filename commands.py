import os

import char
import cli
import dataloaders
import spellbook
import tracker
import utilities


def exit_app(context):
    if context.get_arg(0) != "nosave":
        context.save()

    raise SystemExit


def save(context):
    if context.character:
        context.save()
        print(
            "Successfully saved "
            f"{utilities.capitalise(context.character.name)}."
        )
    else:
        print('No current character to save. Start one with "ch"!')


def info(context):
    spell = context.spellbook.get_spell(context.arg_text)
    if spell:
        opt = cli.print_spell(
            spell,
            cli.get_width(context.config["use_full_width"]),
            context.config["print_spell_classes"],
            context.config["print_spell_rolls"],
        )
        context.update_options(opt)
    else:
        print("Sorry, I couldn't find that spell.")


def search(context):
    try:
        spells = context.spellbook.handle_query(context.arg_text)
    except ValueError as e:
        print(f"Invalid search. {e}")
        return

    if spells:
        if len(spells) == 1:
            opt = cli.print_spell(
                spells[0],
                cli.get_width(context.config["use_full_width"]),
                context.config["print_spell_classes"],
                context.config["print_spell_rolls"],
            )

            context.update_options(opt)
        else:
            spell_names = [spell.name for spell in spells]
            cli.print_list("Results", spell_names)
            context.update_options(("spell", spell_names))
    else:
        print("Couldn't find any spells matching that description.")


def roll(context):
    context.update_roll(utilities.parse_roll(context.get_arg(0)))


def reroll(context):
    rerolls = []
    for die in context.args:
        if die.isnumeric() and int(die) <= len(context.previous_roll):
            rerolls.append(int(die))
        else:
            print(
                'Usage: "rr <dice> <to> <re> <roll>", where dice are '
                + "identified by their index."
            )
            break
    else:
        result = utilities.reroll(
            context.previous_roll, context.previous_roll_die, rerolls
        )
        context.update_roll(result)


def characters(context):
    context.update_options(cli.print_chars())


def delchar(context):
    dataloaders.delete_character(utilities.capitalise(context.arg_text))


def clear_screen(_):
    utilities.clear_screen()


def tracker_access(context):
    if not context.character_check(True):
        return

    name = context.get_arg(0)
    if name in mapping:
        print(f'Name "{name}" is a command and thus reserved.')
    elif name and name.isnumeric():
        print("Numbers are used to select options and thus reserved.")
    elif name in context.character.trackers:
        if context.arg_count() > 1:
            t = context.character.trackers[name]
            print(t.handle_command(context.args[1:]))
        else:
            print(context.character.trackers[name])
    elif context.arg_count() == 1:
        context.character.trackers[name] = tracker.Tracker(name)
    elif (
        context.arg_count() == 3
        and context.get_arg(1) == "="
        and context.get_arg(2).isnumeric()
    ):

        t = tracker.Tracker(name, default=int(context.get_arg(2)))
        context.character.trackers[name] = t
    else:
        if context.character.trackers:
            context.character.print_trackers()
        else:
            print('Usage: "tracker <name>" or "tracker <name> = <number>".')


def deltracker(context):
    if not context.character_check():
        print("No current character, cannot delete tracker.")
        return

    name = context.get_arg(0)
    if not name:
        print('Usage: "dt <name".')
        return

    try:
        del context.character.trackers[name]
        print(f'Tracker "{name}" deleted.')
    except KeyError:
        print(f'Tracker "{name}" does not exist.')


def character(context):
    name = context.get_arg(0)

    if not name:
        if not context.character_check():
            context.character = char.Char.from_wizard()
        else:
            print(f"Current character: {str(context.character)}.")
        return

    if context.character_check() and cli.get_decision(
        "Current character: "
        + f"{context.character.name}. Save this character?"
    ):

        context.save()

    try:
        data = dataloaders.load_character(name)
        data.update({"sb": context.spellbook})
        context.character = char.Char.from_json(data)
        print(f"Character loaded: {str(context.character)}.")
    except FileNotFoundError:
        print(f"No character {name} found.")


def newchar(context):
    if context.character_check() and cli.get_decision(
        "Current character: "
        + f"{context.character.name}. Save this character?"
    ):

        context.save()

    context.character = char.Char.from_wizard()


def prepare(context):
    if not context.character_check(True):
        print('To prepare spells, start a character with "char".')
        return

    if not context.has_args():
        print('Usage: "p <spell>".')
        return

    spell = context.spellbook.get_spell(context.arg_text)
    if spell:
        context.character.prepare_spell(spell)
    else:
        print("Sorry, I couldn't find that spell.")


def prepared(context):
    if context.character_check():
        context.update_options(cli.print_prepped(context.character))
    else:
        print('To prepare spells, start a character with "char".')


def cast(context):
    if not context.character_check():
        print('To cast spells, start a character with "char".')
        return

    if not context.has_args():
        print('Usage: "c <spell>" or "c <level>".')
        return

    spell = context.arg_text
    if spell.isnumeric():
        spell = spellbook.Spell.from_json(
            {
                "name": f"a {utilities.level_prefix(int(spell))} Spell",
                "level": int(spell),
                "school": "placeholder",
            }
        )
    else:
        spell = context.spellbook.get_spell(spell)

    if spell:
        context.character.cast_spell(spell)
    else:
        print(f"No spell {context.arg_text} found.")


def slots(context):
    if context.character_check():
        context.character.print_spell_slots()
    else:
        print('No current character. Start one with "char".')


def rename(context):
    if not context.has_args():
        print('Usage: "rename <new name>"')
    elif not context.character_check():
        print('No current character to rename. Start or load one with "char".')
    else:
        old_name = context.character.name
        context.character.name = context.arg_text
        print(
            f"Renamed {utilities.capitalise(old_name)} to "
            + f"{utilities.capitalise(context.arg_text)}."
        )

        if dataloaders.save_exists(old_name) and cli.get_decision(
            "Delete " + f"old save file for {utilities.capitalise(old_name)}?"
        ):

            dataloaders.delete_character(old_name)


def rest(context):
    if context.character_check():
        context.character.long_rest()
    else:
        print('To rest, start or load a character with "char".')


def level_up(context):
    if context.has_args():
        if context.get_arg(0) == "up":
            if context.arg_count() == 1:
                context.character.level_up()
            elif context.arg_count() == 2:
                context.character.level_up(context.get_arg(1))
        elif context.command == "levelup":
            context.character.level_up(context.get_arg(0))
        else:
            print('Usage: "levelup" or "levelup <class>".')
    else:
        context.character.level_up()


def settings(context):
    options = [setting for setting in context.config]
    state_list = [f"{opt}: {context.config[opt]}" for opt in options]
    cli.print_list(
        "Settings", state_list, "Select an option to toggle that setting."
    )
    context.update_options(("setting", options))


def load(context):
    try:
        data = dataloaders.load_character_from_path(context.raw_text)
    except FileNotFoundError:
        print(f'Failed to load path "{context.raw_text}".')
        return

    if context.character_check() and cli.get_decision(
        "Current character: "
        + f"{context.character.name}. Save this character?"
    ):

        context.save()

    context.save_file = os.path.abspath(context.raw_text)
    data["sb"] = context.spellbook
    context.character = char.Char.from_json(data)
    print(f"Character loaded: {str(context.character)}.")


mapping = {
    "exit": exit_app,
    "save": save,
    "info": info,
    "i": info,
    "search": search,
    "s": search,
    "roll": roll,
    "reroll": reroll,
    "rr": reroll,
    "characters": characters,
    "chars": characters,
    "delchar": delchar,
    "clear": clear_screen,
    "cls": clear_screen,
    "tracker": tracker_access,
    "t": tracker_access,
    "deltracker": deltracker,
    "dt": deltracker,
    "character": character,
    "char": character,
    "ch": character,
    "newchar": newchar,
    "prepare": prepare,
    "prep": prepare,
    "p": prepare,
    "prepared": prepared,
    "prepped": prepared,
    "pd": prepared,
    "cast": cast,
    "c": cast,
    "slots": slots,
    "rename": rename,
    "rest": rest,
    "levelup": level_up,
    "level": level_up,
    "settings": settings,
    "load": load,
}
