import os
import re

import roll

import char
import cli
import constants
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


def roll_dice(context):
    rolls = roll.get_rolls(context.arg_text)
    if rolls:
        print(roll.rolls_string(rolls))
        context.update_roll(rolls[-1])
    else:
        print('Usage: "roll d20a + 6"')


def reroll(context):
    n = context.get_arg(0)
    if n.isnumeric():
        old_total = context.previous_roll.total
        context.previous_roll.reroll(int(n))
        delta = context.previous_roll.total - old_total
        delta_string = ("+" if delta > 0 else "") + str(delta)
        print(str(context.previous_roll) + f" ({delta_string})")
    else:
        print('Usage: "reroll <number of dice>"')


def characters(context):
    context.update_options(cli.print_chars())


def delchar(context):
    dataloaders.delete_character(utilities.capitalise(context.arg_text))


def clear_screen(_):
    utilities.clear_screen()


# Returns the name of the tracker being handled, or None if no further
# processing should occur.
def common_tracker_handling(context):
    if not context.character_check(True):
        return

    name = context.get_arg(0)
    if name in mapping:
        print(f'Name "{name}" is a command and thus reserved.')
    elif name and name.isnumeric():
        print("Numbers are used to select options and thus reserved.")
    elif t := context.get_tracker(name):
        if context.arg_count() > 1:
            print(t.handle_command(context))
        else:
            print(t)
    elif context.arg_count() == 0:
        context.character.print_trackers()
    else:
        return name


def tracker_access(context):
    name = common_tracker_handling(context)
    if name is None:
        return

    if tracker.TrackerCollection.TRACKER_ACCESS_OPERATOR in name:
        names = name.split(tracker.TrackerCollection.TRACKER_ACCESS_OPERATOR)
        tc = context.get_tracker(names=names[:-1])
        tc_name = ".".join(names[:-1])

        if tc is None:
            print(f'No collection "{tc_name}".')
            return
        elif not isinstance(tc, tracker.TrackerCollection):
            print(f"{tc_name} is not a collection.")
            return
        name = names[-1]
    else:
        tc = None

    if not name.isalnum():
        print("Tracker names must be alphanumeric.")
        return
    elif context.arg_count() == 1:
        t = tracker.Tracker(name=name)
    elif (
        context.arg_count() == 3
        and context.get_arg(1) == "="
        and context.get_arg(2).isnumeric()
    ):
        t = tracker.Tracker(name=name, default=int(context.get_arg(2)))
    else:
        print('Usage: "tracker <name>" or "t <name> = <integer>".')
        return

    if tc is not None:
        tc.add_tracker(t)
        print(f"Created tracker {tc_name}.{t.name}.")
    else:
        t.add_to_char(context.character)
        print(f"Created tracker {t.name}.")


def tracker_collection(context):
    name = common_tracker_handling(context)
    if name is None:
        return
    elif context.arg_count() == 1:
        if not name.isalnum():
            print("Tracker collection names must be alphanumeric.")
        elif name in tracker.tracker_collection_presets and cli.get_decision(
            f'There is a collection preset for "{name}". Use this?'
        ):
            tracker.tracker_collection_presets[name]().add_to_char(
                context.character
            )
        else:
            tracker.TrackerCollection(name=name).add_to_char(context.character)
        print(f"Created tracker collection {name}.")
    else:
        print('Usage: "tc <name>".')


def deltracker(context):
    if not context.character_check():
        print("No current character, cannot delete tracker.")
        return

    name = context.get_arg(0)
    if not name:
        print('Usage: "dt <name".')
        return

    try:
        names = tracker.TrackerCollection.expand_name(name)

        if len(names) == 1:
            try:
                context.character.trackers.delete_child(names[0])
            except KeyError:
                print(
                    f"Couldn't find {name}. If it's part of a collection,"
                    " remember to specify which one through "
                    '"dt <parent>.<child>"'
                )
        else:
            parent = context.get_tracker(names=names[:-1])
            if parent:
                parent.delete_child(names[-1])
                print(f'Tracker "{name}" deleted.')
            else:
                print(
                    "Couldn't find the tracker "
                    + tracker.TrackerCollection.TRACKER_ACCESS_OPERATOR.join(
                        names[:-1]
                    )
                    + " to delete {name} from."
                )
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
        "Current character: " f"{context.character.name}. Save this character?"
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
    context.set_char(char.Char.from_wizard(), save_check=True)


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
        print("\n".join(context.character.long_rest()))
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
    if (setting := context.get_arg(0)) in constants.DEFAULT_CONFIG:
        if isinstance(context.config[setting], bool):
            context.config[setting] = not context.config[setting]
            print(f"Toggled {setting} to {context.config[setting]}.")
        else:  # currently, all settings are boolean or string
            context.config[setting] = cli.get_input("New text editor")
    else:
        options = [setting for setting in context.config]
        state_list = [f"{opt}: {context.config[opt]}" for opt in options]
        cli.print_list(
            "Settings", state_list, "Select an option to edit that setting."
        )
        context.update_options(("setting", options))


def load(context):
    try:
        if context.arg_count():
            path = context.raw_text.replace("load", "", 1).strip()
        else:
            path = cli.get_choice("Load which save?", context.save_files)
        data = dataloaders.load_character_from_path(path)
    except FileNotFoundError:
        print(f'Failed to load path "{path}".')
        if path in context.save_files:
            context.save_files.remove(path)
        return

    if context.character_check() and cli.get_decision(
        "Current character: "
        + f"{context.character.name}. Save this character?"
    ):

        context.save()

    context.save_file = os.path.abspath(path)
    data["sb"] = context.spellbook
    context.character = char.Char.from_json(data)
    print(f"Character loaded: {str(context.character)}.")


def load_orcbrew(context):
    path = context.raw_text.replace("load_orcbrew", "", 1).strip()
    dataloaders.load_orcbrew(path, context.spellbook)


def stats(context):
    if not context.character_check(True):
        return

    if context.character.stats is None:
        if cli.get_decision(
            f"{context.character.name} has no stats. Add them?"
        ):
            context.character.stats = char.Stats.from_wizard()

    if context.arg_count() and context.get_arg(0) == "update":
        context.character.stats.update_stat_wizard()
    else:
        print(
            f"\n"
            + context.character.stats.indented_string(
                context.character.name + "'s stats"
            )
            + "\n"
        )


def notes(context):
    cli.print_list(
        "Notes: ",
        [
            n.partition("\n")[0] if "\n" in n else n
            for n in context.character.notes
        ],
        truncate_to=cli.get_width(context.config["use_full_width"]),
    )
    context.update_options(("note", context.character.notes))


def note(context):
    if not context.character_check(True):
        return

    if context.arg_count() == 1 and context.get_arg(0).isnumeric():
        if len(context.character.notes) >= (i := int(context.get_arg(0)) - 1):
            print(context.character.notes[i])
            print("\n[1] Edit [2] Delete")
            context.update_options(
                (
                    "func",
                    [
                        lambda: context.character.replace_note(
                            i, t  # pylint: disable=undefined-variable
                        )
                        if (
                            t := cli.get_text_editor(
                                default=context.character.notes[i],
                                editor=context.config["note_editor_program"],
                            ).strip()
                        )
                        else None,
                        lambda: context.character.remove_note(i),
                    ],
                )
            )
        else:
            print(
                f"You only have {len(context.character.notes)} notes"
                f" for {context.character.name}."
            )
    else:
        note = cli.get_text_editor(
            editor=context.config["note_editor_program"]
        ).strip()
        if note:
            context.character.add_note(note)


mapping = {
    "exit": exit_app,
    "save": save,
    "info": info,
    "i": info,
    "search": search,
    "s": search,
    "roll": roll_dice,
    "reroll": reroll,
    "rr": reroll,
    "characters": characters,
    "chars": characters,
    "delchar": delchar,
    "clear": clear_screen,
    "cls": clear_screen,
    "tracker": tracker_access,
    "t": tracker_access,
    "collection": tracker_collection,
    "tc": tracker_collection,
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
    "load_orcbrew": load_orcbrew,
    "stats": stats,
    "notes": notes,
    "note": note,
}
