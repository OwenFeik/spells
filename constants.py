SPELLSLOTS = {
    0: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}

CASTER_TYPES = {
    "artificer": 0.5,
    "barbarian": 0,
    "bard": 1,
    "cleric": 1,
    "druid": 1,
    "fighter": 0,
    "monk": 0,
    "paladin": 0.5,
    "ranger": 0.5,
    "rogue": 0,
    "sorcerer": 1,
    "warlock": 0,
    "wizard": 1,
    "non": 0,
    "half": 0.5,
    "full": 1,
}

DEFAULT_CONFIG = {
    "print_spell_classes": True,
    "print_spell_rolls": True,
    "load_previous_char": True,
    "use_full_width": False,
    "print_stack_traces": False,
}

DEFAULT_SPELLBOOK_URL = (
    "https://raw.githubusercontent.com/OwenFeik/spells_data/master/spells.json"
)
