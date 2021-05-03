#!/bin/python3

import dataloaders

dataloaders.ensure_module_installed("roll")

import char
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

try:
    while True:
        context.get_input()
        try:
            context.handle_command()
        except KeyboardInterrupt:
            print(
                "\n^C again to exit without saving, or use"
                ' "exit" to exit gracefully.'
            )
except KeyboardInterrupt:
    print()
