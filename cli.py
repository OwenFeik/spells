import os  # get_terminal_size
import re
import dataloaders
import subprocess  # notes editor
import tempfile  # notes editor
import utilities


PS = "> "
TRUNCATED = "..."

# Text editing on linux is done through tempfile
EDITOR_ENVIRONMENT_VARIABLE = "EDITOR"
EDITOR_FALLBACK = "vim" if os.name == "posix" else "notepad"

# On windows, create a text file and have the user edit it
EDITOR_FILE_PATH = "resources/note.txt"


def print_spell(spell, width=None, print_classes=True, options=True):
    if width is None:
        width = get_width()

    out = ""

    if spell.level == 0:
        school = spell.school + " Cantrip"
    else:
        school = f"{utilities.level_prefix(spell.level)} {spell.school}"

    if len(spell.name) + len(school) < width:
        out = f"\n{spell.name} | {school}"
    else:
        out = f"\n{spell.name}\n{school}"

    if spell.ritual:
        if len(spell.cast) + len(spell.range) + 33 < width:
            out += (
                f"\nCasting Time: {spell.cast} | Ritual | Range: {spell.range}"
            )
        else:
            out += (
                f"\nCasting Time: {spell.cast} | Ritual\nRange: {spell.range}"
            )
    else:
        if len(spell.cast) + len(spell.range) + 24 < width:
            out += f"\nCasting Time: {spell.cast} | Range: {spell.range}"
        else:
            out += f"\nCasting Time: {spell.cast}\nRange: {spell.range}"

    if len(spell.components) + len(spell.duration) + 25 < width:
        out += f"\nComponents: {spell.components} | Duration: {spell.duration}"
    else:
        components = utilities.printable_paragraph(
            "Components: " + spell.components, width
        )
        duration = utilities.printable_paragraph(
            "Duration: " + spell.duration, width
        )
        out += f"\n{components}\n{duration}"

    desc = spell.desc
    if options:
        temp_rolls = re.findall(r"(?<!increases by )(\d+d\d+)", desc)
        rolls = []
        for roll in temp_rolls:
            if roll not in rolls:
                rolls.append(roll)

        for i, roll in enumerate(rolls):
            desc = desc.replace(roll, f"{roll} [{i + 1}]", 1)

    out += f"\n{utilities.printable_paragraph(desc, width)}\n"

    if print_classes:
        classes = ", ".join(spell.classes)
        subclasses = ", ".join(spell.subclasses)

        if classes or subclasses:
            class_str = f"Classes with {spell.name}: "
            if classes:
                class_str += classes
                if subclasses:
                    class_str += ", "
            if subclasses:
                class_str += subclasses
            out += f"\n{utilities.printable_paragraph(class_str, width)}\n"

    print(out)

    if options:
        return "roll", rolls  # opt


def get_width(use_full_width=False):
    width = os.get_terminal_size()[0]
    if not use_full_width:
        if width < 60:
            pass
        elif width < 120:
            width = int(0.8 * width)
        else:
            width = int(0.6 * width)
    return width


def print_prepped(char):
    out = ""
    opt = []

    spells = {i: [] for i in range(0, 10)}

    for spell in sorted(char.prepared, key=lambda k: k.name):
        spells[spell.level].append(spell.name)

    for i in range(0, 10):
        if spells[i]:
            out += f"\n{utilities.level_prefix(i)}:"
            for spell in spells[i]:
                opt.append(spell)
                out += f"\n\t[{len(opt)}] {spell}"
            out += "\n"

    print(out)
    return ("spell", opt)


def print_chars():
    chars = dataloaders.current_chars()
    if chars:
        char_string = ""
        for i in range(len(chars)):
            char_string += f"\n[{i+1}] {chars[i].get('name')} | "
            first = True
            for klasse in chars[i].get("classes"):
                if not first:
                    char_string += ", "
                char_string += (
                    utilities.capitalise(klasse.get("name"))
                    + " "
                    + klasse.get("level")
                )
                first = False
        print(f"\nCharacters:\n{char_string}\n")
        opt = [char.get("name").lower() for char in chars]
        return ("char", opt)
    else:
        print("No characters saved.")


def print_list(title, items, afterword="", truncate_to=None):
    print(f"\n{title}{':' if title[-1].isalpha() else ''}")

    for i, item in enumerate(items):
        line = f"\t[{i + 1}] {item}"
        if truncate_to:
            line = (
                line[: truncate_to - len(TRUNCATED)] + TRUNCATED
                if len(line) > truncate_to
                else line
            )
        print(line)

    if afterword:
        print(f"\n{afterword}")
    print()


def get_input(prompt, split=False, default=None):
    p = prompt
    if default is not None:
        p += f" (default {default})"
    p += f" {PS}"

    string = input(p).strip()

    if not string and default is not None:
        return default
    return string.split() if split else string


def get_decision(prompt, default=True):
    p = f"{prompt} ({'Y' if default else 'y'}/{'n' if default else 'N'}) {PS}"
    resp = input(p).strip().lower()
    return resp == "y" or default and resp == ""


def get_choice(prompt, items, labels_for=None, truncate_to=None):
    print_list(prompt, items, truncate_to=truncate_to)

    choice = input(PS)
    while (
        not (choice.isnumeric() and int(choice) <= len(items))
        and not choice in items
    ):
        choice = input(
            f"Please enter the number of an item from the options {PS}"
        )

    if choice.isnumeric() and (i := int(choice) - 1) < len(items):
        pass
    elif choice in items:
        i = items.index(choice)

    if labels_for:
        return labels_for[i]
    return items[i]


def get_integer(prompt, default=None):
    p = f"{prompt} (number"
    if default is not None:
        p += f", default {default}"
    p += f") {PS}"

    while not ((v := input(p)).isnumeric() or (v := default) is not None):
        print("Please enter a number.")

    return int(v)


def get_text_editor_posix(default, editor):
    with tempfile.NamedTemporaryFile(suffix=".txt") as tf:
        tf.write(default.encode())
        tf.flush()
        subprocess.call(
            [
                editor,
                tf.name,
            ]
        )
        tf.seek(0)
        return tf.read().decode()


def get_text_editor_nt(default, editor):
    path = dataloaders.get_real_path(EDITOR_FILE_PATH)
    with open(path, "w") as f:
        f.write(default)

    subprocess.call([editor, path], shell=True)

    with open(path, "r") as f:
        return f.read()


def get_text_editor(default="", editor=None):
    if editor is None:
        editor = os.environ.get(EDITOR_ENVIRONMENT_VARIABLE, EDITOR_FALLBACK)

    if os.name == "posix":
        return get_text_editor_posix(default, editor)
    elif os.name == "nt":
        return get_text_editor_nt(default, editor)
