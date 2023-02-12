import collections
import time

import roll

import cli
import utilities


class RollHistory:
    DEFAULT_SIZES = [4, 6, 8, 10, 12, 20]

    def __init__(self, rolls=None):
        self.rolls = rolls or collections.defaultdict(lambda: [])

    def log_roll(self, robj):
        for (r, results) in robj.roll_info():
            _, die = r.split(roll.RollToken.SEPERATOR)
            self.rolls[int(die)].append((results, time.time()))

    def rolls_before(self, die, start_time):
        return [
            r
            for (results, t) in self.rolls[die]
            if t >= start_time
            for r in results
        ]

    def stat_string(self, start_time=0, die=None):
        table = []
        for die in die or RollHistory.DEFAULT_SIZES:
            rolls = self.rolls_before(die, start_time)
            if rolls:
                avg = round(sum(rolls) / len(rolls), 2)
                delta = round((avg - (1 + die) / 2), 2)
                delta_str = utilities.mod_str(delta) if delta else "(avg)"
            else:
                avg = 0.0
                delta_str = "(avg)"
            table.append(
                [
                    f"{roll.RollToken.SEPERATOR}{die}",
                    f"{str(len(rolls))} rolled",
                    str(avg),
                    delta_str,
                ]
            )
        return cli.format_table(table)

    def to_json(self):
        return {"rolls": self.rolls}

    @staticmethod
    def from_json(data):
        return RollHistory(
            collections.defaultdict(
                lambda: [], {int(k): v for k, v in data["rolls"].items()}
            )
        )
