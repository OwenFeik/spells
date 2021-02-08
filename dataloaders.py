import importlib
import json
import os
import subprocess
import sys
import urllib.request
import warnings

import cli
import constants
import spellbook
import utilities


def get_real_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


def get_spellslots(level):
    return constants.SPELLSLOTS[level]


def get_spells(resource_dir="resources", prompt_download=True):
    spells_file = get_real_path(resource_dir + "/spells.json")

    if not os.path.exists(spells_file):
        if prompt_download and cli.get_decision(
            "No spellbook found. Download default?"
        ):
            with urllib.request.urlopen(constants.DEFAULT_SPELLBOOK_URL) as f:
                data = f.read().decode("utf-8")
                with open(spells_file, "w") as f:
                    f.write(data)

    with open(spells_file, "r") as f:
        return json.load(f)


def load_character(name):
    return load_character_from_path(get_real_path(f"saves/{name.lower()}.json"))


def save_character(char, path=""):
    if not path:
        path = get_real_path(f"saves/{char.name.lower()}.json")

    if not os.path.exists(get_real_path("saves")):
        os.mkdir(get_real_path("saves"))

    with open(path, "w") as f:
        json.dump(char.to_json(), f, indent=4)

    return path


def delete_character(char):
    char_file = get_real_path(f"saves/{char.lower()}.json")
    if os.path.exists(char_file):
        os.remove(char_file)
        print(f"Deleted character {char}.")
    else:
        print(f'No character "{char}" found.')


def load_character_from_path(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Character located at {path} corrupted.")
                return None
    raise FileNotFoundError


def current_chars():
    saves = os.listdir(get_real_path("saves"))
    chars = []
    for save in saves:
        if ".json" in save:
            with open(get_real_path(f"saves/{save}"), "r") as f:
                chars.append(json.load(f))
    return chars


def save_exists(name):
    names = [c["name"] for c in current_chars()]
    return name.lower() in names


def get_cache():
    try:
        with open(get_real_path("resources/cache.json"), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {"character": None}


def save_cache(path=None):
    resources_path = get_real_path("resources")
    if not os.path.exists(resources_path):
        os.mkdir(resources_path)

    with open(resources_path + "/cache.json", "w") as f:
        json.dump({"character": path}, f)


def clear_cache():
    cache_path = get_real_path("resources/cache.json")
    if os.path.exists(cache_path):
        os.remove(cache_path)


def get_config():
    try:
        with open(get_real_path("resources/config.json"), "r") as f:
            cfg = json.load(f)

        # If a setting is missing from the config, use the default
        for setting in constants.DEFAULT_CONFIG:
            if setting not in cfg:
                cfg[setting] = constants.DEFAULT_CONFIG[setting]

        return cfg
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return constants.DEFAULT_CONFIG


def save_config(config):
    with open(get_real_path("resources/config.json"), "w") as f:
        json.dump(config, f, indent=4)


def ensure_module_installed(module):
    try:
        importlib.import_module(module)

        return
    except ImportError:
        if not cli.get_decision(
            f'No installation of "{module}" '
            "Attempt automatic dependency install?"
        ):
            print("Exiting due to missing module.")
            raise SystemExit

    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-U",
                "-r",
                get_real_path("requirements.txt"),
            ]
        )
        importlib.import_module(module)
    except (subprocess.CalledProcessError, ImportError):
        print(
            f'Failed to automatically install "{module}". Run '
            '"python -m pip install -U -r requirements.txt" '
            " in install directory to install dependencies."
        )
        raise SystemExit


def load_orcbrew(path, sb):
    ensure_module_installed("edn_format")
    import edn_format

    try:
        with open(path, "rb") as f:
            binary = f.read()
            data = edn_format.loads(binary.decode("utf-8", "ignore"))
    except FileNotFoundError:
        print(f'Couldn\'t find an orcbrew at "{path}".')
        return
    except edn_format.EDNDecodeError:
        print("Failed to read the orcbrew file.")
        return

    spells = data[edn_format.Keyword("orcpub.dnd.e5/spells")]

    keywords = {
        kw: edn_format.Keyword(kw)
        for kw in [
            "name",
            "school",
            "level",
            "casting-time",
            "range",
            "duration",
            "components",
            "verbal",
            "somatic",
            "material",
            "material-component",
            "duration",
            "description",
            "spell-lists",
        ]
    }

    classes = {
        kw: edn_format.Keyword(kw.lower())
        for kw in [
            "Bard",
            "Cleric",
            "Druid",
            "Paladin",
            "Ranger",
            "Sorcerer",
            "Warlock",
            "Wizard",
        ]
    }

    kw = lambda w: keywords[w]

    new_spells = []
    for spell in spells.values():
        spell_json = {
            w: utilities.replace_unicode(spell[kw(w)])
            if type(spell[kw(w)]) == str
            else spell[kw(w)]
            for w in [
                "name",
                "school",
                "level",
                "casting-time",
                "range",
                "description",
            ]
        }

        if kw("duration") in spell:
            spell_json["duration"] = spell[kw("duration")]
        else:
            spell_json["duration"] = "Instantaneous"

        spell_json["cast"] = spell_json["casting-time"]
        del spell_json["casting-time"]

        components = spell[kw("components")]
        component_string = ", ".join(
            [
                c[0].upper()
                for c in ["verbal", "somatic", "material"]
                if components.get(kw(c))
            ]
        )
        material = components.get(kw("material-component"))
        if material:
            component_string += f" ({material})"

            # some of the entries end in a closing bracket
            # for no discernible reason.
            if component_string[-2:] == "))" and component_string.count(
                "("
            ) != component_string.count(")"):

                component_string = component_string[:-1]
        spell_json["components"] = component_string

        spell_classes = []
        spell_lists = spell[kw("spell-lists")]
        for c in classes:
            if spell_lists[classes[c]]:
                spell_classes.append(c)
        spell_json["classes"] = spell_classes

        spell_json["ritual"] = False
        spell_json["alt_names"] = []
        spell_json["subclasses"] = []

        new_spells.append(spellbook.Spell.from_json(spell_json))

    if cli.get_decision(
        f"Found {len(new_spells)} spells. Add these to your spellbook?"
    ):
        sb.add_spells(new_spells)
        if cli.get_decision('Add these spells to "spells.json"?'):
            with open("resources/spells.json", "w") as f:
                json.dump(sb.get_spells_json(), f, indent=4)
