import cli
import roll


class Stats:
    STR = "str"
    DEX = "dex"
    CON = "con"
    INT = "int"
    WIS = "wis"
    CHA = "cha"
    DEFAULT_VALUE = 10
    DND_STATS = [STR, DEX, CON, INT, WIS, CHA]
    DEFAULT_ROLL_FORMAT = "4d6k3"

    def __init__(self, **kwargs):
        for stat in Stats.DND_STATS:
            setattr(self, stat, kwargs.get(stat, Stats.DEFAULT_VALUE))

    def __str__(self):
        return self.indented_string()

    def __getitem__(self, key):
        return getattr(self, key.lower())

    def mod(self, mod_name):
        return (self[mod_name.lower()] - 10) // 2

    def set_stat(self, stat, value):
        setattr(self, stat.lower(), value)

    def indented_string(self, title="Stats"):
        string = f"{title}:\n\t"
        string += "\n\t".join(
            f"{s.upper()}: {getattr(self, s)}" for s in Stats.DND_STATS
        )
        return string

    def update_stat_wizard(self):
        self.set_stat(
            cli.get_choice(
                "Update which stat?", [s.upper() for s in Stats.DND_STATS]
            ),
            cli.get_integer("New score", 10),
        )

    def to_json(self):
        return {s: getattr(self, s) for s in Stats.DND_STATS}

    @staticmethod
    def from_entry_wizard():
        stats = {}

        for stat in Stats.DND_STATS:
            stats[stat] = cli.get_integer(
                stat.upper() + " score", Stats.DEFAULT_VALUE
            )

        return Stats(**stats)

    @staticmethod
    def from_rolling_wizard():
        stats = {}
        remaining_stats = [s.upper() for s in Stats.DND_STATS]

        roll_format = cli.get_input(
            "Stat roll format", default=Stats.DEFAULT_ROLL_FORMAT
        )

        rolls = roll.get_rolls(f"{len(remaining_stats)} {roll_format}")
        print(f"\nYour rolls:\n{roll.rolls_string(rolls)}")
        scores = [str(r.total) for r in sorted(rolls, key=lambda r: r.total)]

        while len(remaining_stats) > 1:
            stat = cli.get_choice(
                "Choose a stat to assign a score to:", remaining_stats
            )
            remaining_stats.remove(stat)

            score = cli.get_choice(f"Choose a score for {stat}", scores)
            scores.remove(score)

            stats[stat.lower()] = int(score)
        stats[remaining_stats[0]] = scores[0]

        return Stats(**stats)

    @staticmethod
    def from_wizard():
        if cli.get_decision("Would you like to roll for stats?", False):
            return Stats.from_rolling_wizard()
        else:
            return Stats.from_entry_wizard()

    @staticmethod
    def from_json(data):
        return Stats(**data)
