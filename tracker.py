import collections
import re
import random

import roll


class AbstractTracker:
    def __init__(
        self, name="", default=None, quantity=None, reset_on_rest=False
    ):
        self.name = name
        self.default = default
        self.quantity = quantity
        self.reset_on_rest = reset_on_rest

    def __repr__(self):
        return (
            f"<AbstractTracker name={self.name} default={self.default} "
            f"quantity={self.quantity} reset_on_rest={self.reset_on_rest}>"
        )

    def __str__(self):
        return self.to_string()

    def parse_args(self, context):
        command, *args = context.args
        command = command.lower()

        if (
            context.command in ["t", "tracker", "tc", "collection"]
            and command == self.name
        ):
            command, *args = args
            command = command.lower()

        return command, args

    def handle_command(self, arguments):
        raise NotImplementedError()

    def reset(self):
        if self.default is not None:
            self.quantity = self.default

    def rest(self):
        if self.reset_on_rest:
            self.reset()

    def add_to_char(self, char):
        char.trackers[self.name] = self

    def to_string(self, indent=0):
        return "\t" * indent + f"{self.name}: {self.quantity}"

    def to_json(self):
        return {
            "type": "AbstractTracker",
            "name": self.name,
            "quantity": self.quantity,
            "default": self.default,
            "reset_on_rest": self.reset_on_rest,
        }

    @staticmethod
    def from_json(data):
        raise NotImplementedError()


class Tracker(AbstractTracker):
    def __init__(self, name="", default=0, quantity=None, reset_on_rest=False):
        super().__init__(
            name,
            default,
            quantity if quantity is not None else default,
            reset_on_rest,
        )

    def __repr__(self):
        return super().__repr__().replace("Abstract", "", 1)

    def handle_command(self, context):
        command, args = self.parse_args(context)

        if command == "reset":
            self.quantity = self.default
            return f"Reset {self.name} to {self.quantity}."
        elif command == "rest":
            self.reset_on_rest = not self.reset_on_rest
            return (
                f"Changed rest reset flag for {self.name}."
                f'Now "{self.reset_on_rest}".'
            )
        elif command == "++":
            self.quantity += 1
            return f"Incremented {self.name}. Current value: {self.quantity}"
        elif command == "--":
            self.quantity -= 1
            return f"Decremented {self.name}. Current value: {self.quantity}"
        elif command == "default" and not args:
            return f"Current default value of {self.name}: {self.default}."
        elif not args:
            return f"If command {command} exists, it requires arguments."

        if args[0].isnumeric():
            quantity = int(args[0])
        else:
            rolls = roll.get_rolls(" ".join(args), max_qty=1)
            if rolls:
                quantity = rolls[0].total
            else:
                return "This command requires you to specify a quantity."

        if command in ["add", "give", "+", "+="]:
            self.quantity += quantity
            return (
                f"Added {quantity} to {self.name}."
                f" Current value: {self.quantity}."
            )
        elif command in ["subtract", "take", "-", "-="]:
            self.quantity -= quantity
            return (
                f"Subtracted {quantity} from {self.name}."
                f"Current value: {self.quantity}."
            )
        elif command in ["set", "="]:
            self.quantity = quantity
            return f"Set {self.name} to {self.quantity}."
        elif command == "default":
            # Allow for t default = 3 as well as t default 3.
            if args[0] == "=" and args[1].isnumeric():
                quantity = int(args[1])

            self.default = quantity
            return f"Set default of {self.name} to {self.default}."
        else:
            return f"Command {command} not found."

    def to_json(self):
        return {**super().to_json(), "type": "Tracker"}

    @staticmethod
    def from_json(data):
        return Tracker(**data)


class TrackerCollection(AbstractTracker):
    def __init__(self, name="", quantity=None, reset_on_rest=False):
        super().__init__(
            name,
            default={},
            quantity={} if quantity is None else quantity,
            reset_on_rest=reset_on_rest,
        )
        self.trackers = self.quantity

    def __repr__(self):
        return f"<TrackerCollection name={self.name} trackers={self.quantity}>"

    def _handle_command(self, context, command, t, args):
        if command == "add":
            self.trackers[t.name] = t
            del context.character.trackers[t.name]
            self.add_child_to_char(context.character, t)
            return f"Added {t.name} to {self.name}."
        elif command == "remove":
            context.character.trackers[t.name] = t
            del self.trackers[t.name]
            self.remove_child_from_char(context.character, t)
            return f"Removed {t.name} from {self.name}."
        raise ValueError(f'Command "{command}" not found.')

    def get_tracker_from_name(self, context, name):
        if name not in context.character.trackers:
            if name not in self.trackers:
                raise ValueError(f"No tracker {name} found.")
            else:
                t = self.trackers[name]
        else:
            t = context.character.trackers[name]

        return t

    def handle_command(self, context):
        command, args = self.parse_args(context)

        if len(args) == 0:
            return f'If command "{command}" exists, it requires a \
                tracker as an argument.'
        try:
            return self._handle_command(
                context,
                command,
                self.get_tracker_from_name(context, args[0]),
                args[1:] if len(args) > 1 else [],
            )
        except ValueError as e:
            return str(e)

    def rest(self):
        for t in self.trackers.values():
            t.rest()

    def add_child_to_char(self, char, child):
        char.trackers[f"{self.name}.{child.name}"] = child

    def remove_child_from_char(self, char, child):
        del char.trackers[f"{self.name}.{child.name}"]

    def add_to_char(self, char):
        char.trackers[self.name] = self
        for t in self.trackers.values():
            self.add_child_to_char(char, t)

    def add_tracker(self, child):
        self.trackers[child.name] = child

    def delete_child(self, name):
        del self.trackers[name]

    def to_string(self, indent=0):
        return "\t" * indent + stringify_tracker_iterable(
            self.trackers.values(), self.name, indent + 1
        )

    def to_json(self):
        return {
            "type": "TrackerCollection",
            "name": self.name,
            "quantity": {k: self.trackers[k].to_json() for k in self.trackers},
            "reset_on_rest": self.reset_on_rest,
        }

    @staticmethod
    def from_json(data):
        if "quantity" in data:
            trackers = data["quantity"]
            data["quantity"] = {t: from_json(trackers[t]) for t in trackers}
        return TrackerCollection(**data)


class CoinCollection(TrackerCollection):
    DENOMINATIONS = ["cp", "sp", "ep", "gp", "pp"]
    DENOMINATION_MAPPING = {
        "cp": 1,
        "sp": 10,
        "ep": 50,
        "gp": 100,
        "pp": 1000,
    }

    def __init__(self, name="", **kwargs):
        self.denoms = CoinCollection.DENOMINATIONS[:]
        if not kwargs.get("electrum_enabled"):
            self.denoms.remove("ep")

        if kwargs.get("quantity") is None:
            kwargs["quantity"] = collections.OrderedDict()
            for c in self.denoms:
                kwargs["quantity"][c] = Tracker(c)
        super().__init__(name, kwargs.get("quantity"), False)

        self.set_regex()

    def set_regex(self):
        self.regex = re.compile(
            r"(?P<q>\d+)(?P<c>" + r"|".join(self.denoms) + r")",
            flags=re.IGNORECASE,
        )

    def parse_currency(self, args):
        if len(args) == 1:
            m = re.match(self.regex, args[0])
            quantity = int(m.group("q"))
            currency = m.group("c")
        elif len(args) == 2:
            if args[0].isnumeric() and args[1] in self.denoms:
                quantity = int(args[0])
                currency = args[1]
            else:
                quantity = currency = None

        if quantity == None or currency == None:
            raise ValueError("Failed to parse currency information.")
        else:
            return quantity, currency

    def balance_trackers(self):
        EPSILON = 1e-10

        # This has some strange behaviour due to rounding errors, hence the
        # rounding to epsilon in a couple of places.

        currencies = list(reversed(self.denoms))
        i = 1
        for c in currencies:
            fractional = round(self.trackers[c].quantity % 1, 10)
            if fractional and i < len(currencies):
                self.trackers[currencies[i]].quantity += (
                    fractional * CoinCollection.DENOMINATION_MAPPING[c]
                ) / CoinCollection.DENOMINATION_MAPPING[currencies[i]]

            if (
                abs(
                    round(self.trackers[c].quantity) - self.trackers[c].quantity
                )
                < EPSILON
            ):
                self.trackers[c].quantity = round(self.trackers[c].quantity)
            else:
                self.trackers[c].quantity = int(self.trackers[c].quantity)

            i += 1

    def spend_currency(self, quantity, currency):
        if self.trackers[currency].quantity >= quantity:
            self.trackers[currency].quantity -= quantity
        else:
            old_quantities = {c: self.trackers[c].quantity for c in self.denoms}

            total_cp = CoinCollection.DENOMINATION_MAPPING[currency] * quantity
            for c in self.denoms:
                tracker_cp = (
                    CoinCollection.DENOMINATION_MAPPING[c]
                    * self.trackers[c].quantity
                )
                if tracker_cp >= total_cp:
                    self.trackers[c].quantity -= (
                        total_cp / CoinCollection.DENOMINATION_MAPPING[c]
                    )
                    total_cp = 0
                elif self.trackers[c].quantity > 0:
                    total_cp -= tracker_cp
                    self.trackers[c].quantity = 0

            if total_cp > 0:
                lacking_coins = (
                    total_cp / CoinCollection.DENOMINATION_MAPPING[currency]
                )
                for c in old_quantities:
                    self.trackers[c].quantity = old_quantities[c]
                return (
                    f"Not enough money. {lacking_coins}{currency} more"
                    " required."
                )
            else:
                self.balance_trackers()
        return (
            f"Spent {quantity}{currency}. Remaining: "
            f"{self.trackers[currency].quantity}{currency}."
        )

    def handle_command(self, context):
        command, args = self.parse_args(context)

        if (len(args) == 0 and command == "enable_electrum") or (
            len(args) == 1
            and command == "enable"
            and args[0] in ["electrum", "ep"]
        ):
            if "ep" in self.denoms:
                return "Electrum pieces are already being used."
            self.denoms.insert(2, "ep")
            self.set_regex()

            self.trackers["ep"] = Tracker("ep")
            self.trackers.move_to_end("gp")
            self.trackers.move_to_end("pp")

            return "Electrum pieces have been enabled."
        elif (len(args) == 0 and command == "disable_electrum") or (
            len(args) == 1
            and command == "disable"
            and args[0] in ["electrum", "ep"]
        ):
            if "ep" in self.denoms:
                self.denoms.remove("ep")
                self.trackers["sp"].quantity += (
                    round(
                        CoinCollection.DENOMINATION_MAPPING["ep"]
                        / CoinCollection.DENOMINATION_MAPPING["sp"]
                    )
                    * self.trackers["ep"].quantity
                )
                del self.trackers["ep"]
                return (
                    "Electrum pieces have been disabled. "
                    "Your electrum has been converted to silver."
                )
            return "Electrum pieces are already disabled."

        try:
            quantity, currency = self.parse_currency(args)
        except ValueError:
            return (
                f'If command "{command}" exists it requires a quantity '
                'and currency like "10gp".'
            )

        if command in ["add", "+", "+="]:
            self.trackers[currency].quantity += quantity
            return (
                f"Added {quantity} to {currency}. Current value: "
                f"{self.trackers[currency].quantity}{currency}."
            )
        elif command in ["spend", "-", "-="]:
            return self.spend_currency(quantity, currency)

    def to_json(self):
        return {
            **super().to_json(),
            "type": "CoinCollection",
            "electrum_enabled": "ep" in self.denoms,
        }

    @staticmethod
    def from_json(data):
        if "quantity" in data:
            trackers = data["quantity"]
            data["quantity"] = collections.OrderedDict(
                {t: from_json(trackers[t]) for t in trackers}
            )
        return CoinCollection(**data)


def from_json(data):
    try:
        tracker_type = data.pop("type")
    except KeyError:
        tracker_type = "Tracker"

    return {
        "AbstractTracker": AbstractTracker,
        "Tracker": Tracker,
        "TrackerCollection": TrackerCollection,
        "CoinCollection": CoinCollection,
    }[tracker_type].from_json(data)


def stringify_tracker_iterable(trackers, heading="Trackers", indent=1):
    tracker_string = "\n" + "\n".join([t.to_string(indent) for t in trackers])
    return f"{heading}:{tracker_string}"


def print_tracker_iterable(trackers):
    print(f"\n{stringify_tracker_iterable(trackers)}\n")


tracker_collection_presets = {
    "coins": lambda: CoinCollection("coins"),
    "wealth": lambda: CoinCollection("wealth"),
}
