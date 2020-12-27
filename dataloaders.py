import json
import os  # Check files in saves folder

import constants


def get_real_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


def get_spellslots(level):
    return constants.spellslots[level]


def get_spells():
    with open(get_real_path("resources/spells.json"), "r") as f:
        return json.load(f)


def load_character(name):
    with open(get_real_path(f"saves/{name.lower()}.json"), "r") as f:
        return json.load(f)


def save_character(char, path=""):
    if not path:
        path = get_real_path(f"saves/{char.name.lower()}.json")

    if not os.path.exists(get_real_path("saves")):
        os.mkdir(get_real_path("saves"))

    with open(path, "w") as f:
        json.dump(char.to_json(), f, indent=4)

    return path


def delete_character(char):
    char_file = get_real_path(f"saves/{char}.json")
    if os.path.exists(char_file):
        os.remove(char_file)
        print(f"Deleted character {char}.")
    else:
        print(f'No character "{char}" found.')


def load_character_from_path(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
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
        for setting in constants.default_config:
            if setting not in cfg:
                cfg[setting] = constants.default_config[setting]

        return cfg
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return constants.default_config


def save_config(config):
    with open(get_real_path("resources/config.json"), "w") as f:
        json.dump(config, f, indent=4)
