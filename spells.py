#!/bin/python3
import readline  # allow use of arrow keys etc in app

import dataloaders

dataloaders.ensure_module_installed("roll")

import char
import cli
import context
import spellbook

try:
    try:
        sb = spellbook.Spellbook()  # Utility for retrieving spell information
    except ValueError:
        print("Spellbook file corrupted. No Spellbook available.")
        sb = None
except FileNotFoundError:
    print("Warning: No Spellbook available.")
    sb = None

cache = dataloaders.get_cache()
cfg = dataloaders.get_config()
c = None  # Current player character

if cfg["load_previous_char"] and cache["character"]:
    try:
        data = dataloaders.load_character_from_path(cache["character"])
        if data is not None:
            data.update({"sb": sb})
            c = char.Char.from_json(data)
            print(f"Character loaded: {str(c)}.")
    except FileNotFoundError:
        pass

context = context.Context(sb, cfg, c)
if c is not None:
    context.save_file = cache["character"]

graceless = False  # allow ^C to exit if user has been warned
while True:
    try:
        context.get_input()
        graceless = False
    except KeyboardInterrupt:  # Handle ^C during input
        print()

        try:
            if graceless or cli.get_decision("Exit gracelessly?"):
                exit()
        except KeyboardInterrupt:  # Allow repeated ^C to confirm
            print()
            exit()

    try:
        context.handle_command()
    except KeyboardInterrupt:  # Allow breaking out of dialogs with ^C
        print(
            " Command cancelled."
            "\n^C again to exit without saving, or use"
            ' "exit" to exit gracefully.'
        )
        graceless = True
