import collections
import enum
import re

import roll

import cli


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

        if context.command in ["t", "tracker", "tc", "collection"] and (
            command == self.name or re.match(rf"\w+\.{self.name}", command)
        ):
            command, *args = args
            command = command.lower()

        return command, args

    def handle_command(self, context):
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
            "type": self.__class__.__name__,
            "name": self.name,
            "quantity": self.quantity,
            "default": self.default,
            "reset_on_rest": self.reset_on_rest,
        }

    @staticmethod
    def from_json(data):
        raise NotImplementedError()


class TrackerCommandOptions(enum.Enum):
    QUANTITY = enum.auto()  # require a number as an argument
    OPTIONAL = enum.auto()  # make argument optional
    ALLOW_EQUALS = enum.auto()  # allow format "command = argument"


class TrackerCommand:
    MISSING_ARG_MESSAGE = "This command requires an integer as an argument."

    def __init__(self, names, options, func):
        self.names = names
        self.needs_quantity = TrackerCommandOptions.QUANTITY in options
        self.arg_optional = TrackerCommandOptions.OPTIONAL in options
        self.arg_allow_equals = TrackerCommandOptions.ALLOW_EQUALS in options
        self.func = func

    def handle(self, args, character=None):
        if not args:
            if not self.needs_quantity or self.arg_optional:
                return self.func()
            else:
                return TrackerCommand.MISSING_ARG_MESSAGE

        quantity = None
        if args[0].isnumeric():
            quantity = int(args[0])
        else:
            rolls = roll.get_rolls(" ".join(args), max_qty=1)
            if rolls:
                quantity = rolls[0].total

        if quantity:
            return self.func(quantity)
        elif (
            self.arg_allow_equals
            and len(args) >= 2
            and args[0] == "="
            and args[1].isnumeric()
        ):
            return self.func(int(args[1]))
        else:
            return TrackerCommand.MISSING_ARG_MESSAGE


class Tracker(AbstractTracker):
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("name", ""),
            kwargs.get("default"),
            kwargs.get("quantity", kwargs.get("default", 0)),
            kwargs.get("reset_on_rest"),
        )
        self.maximum = kwargs.get("maximum")
        self.minimum = kwargs.get("minimum")
        self.commands = self.create_default_commands()

    def __repr__(self):
        return super().__repr__().replace("Abstract", "", 1)

    def create_default_commands(self):
        return [
            TrackerCommand(["reset"], [], self.reset),
            TrackerCommand(["rest"], [], self.rest),
            TrackerCommand(["++"], [], lambda: self.add(1)),
            TrackerCommand(["--"], [], lambda: self.remove(1)),
            TrackerCommand(
                ["default"],
                [
                    TrackerCommandOptions.QUANTITY,
                    TrackerCommandOptions.OPTIONAL,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_default,
            ),
            TrackerCommand(
                ["add", "give", "+", "+="],
                [TrackerCommandOptions.QUANTITY],
                self.add,
            ),
            TrackerCommand(
                ["subtract", "take", "-", "-="],
                [TrackerCommandOptions.QUANTITY],
                self.add,
            ),
            TrackerCommand(
                ["set", "="],
                [
                    TrackerCommandOptions.QUANTITY,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_quantity,
            ),
            TrackerCommand(
                ["min", "minimum"],
                [
                    TrackerCommandOptions.QUANTITY,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_minimum,
            ),
            TrackerCommand(
                ["max", "maximum"],
                [
                    TrackerCommandOptions.QUANTITY,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_maximum,
            ),
        ]

    def add_command(self, command):
        self.commands.append(command)

    def add_command_name(self, name, new):
        target = None
        for c in self.commands:
            if name in c.names:
                target = c
            if new in c.names:
                raise ValueError(f"A command with name {new} already exists.")
        target.names.append(new)

    def remove_command(self, name):
        remove = []
        for c in self.commands:
            if name in c.names:
                remove.append(c)

        for c in remove:
            self.commands.remove(c)

    def reset(self):
        super().reset()

        if self.default is not None:
            return f"Reset {self.name} to {self.quantity}."
        else:
            return f"{self.name} has no default to reset to."

    def bounds_check(self, enforce=True, value=None):
        if value is None:
            value = self.quantity
        else:
            enforce = False

        if self.maximum is not None and value > self.maximum:
            if enforce:
                self.quantity = self.maximum
                return f"Now at maximum: {self.maximum}."
            else:
                return f"Warning: over maximum of {self.maximum}."
        elif self.minimum is not None and value < self.minimum:
            if enforce:
                self.quantity = self.minimum
                return f"Now at minimum: {self.minimum}."
            else:
                return f"Warning: below minimum of {self.minimum}."

    def add(self, quantity):
        self.quantity += quantity
        message = f"Added {quantity} to {self.name}. "

        if (m := self.bounds_check()) :
            message += m
        else:
            message += f"Current value: {self.quantity}."

        return message

    def remove(self, quantity):
        self.quantity -= quantity
        message = f"Took {quantity} from {self.name}. "

        if (m := self.bounds_check()) :
            message += m
        else:
            message += f"Current value: {self.quantity}."

    def toggle_rest_behaviour(self):
        self.reset_on_rest = not self.reset_on_rest
        return (
            f"Changed rest reset flag for {self.name}."
            f" Now {self.reset_on_rest}."
        )

    def set_default(self, quantity=None):
        if quantity is None:
            return f"Current default value of {self.name}: {self.default}."

        self.default = quantity
        message = f"Set default of {self.name} to {self.default}."
        if (m := self.bounds_check(value=self.default)) :
            message += f" {m}"
        return message

    def set_quantity(self, quantity):
        self.quantity = quantity
        message = f"Set {self.name} to {quantity}."

        if (m := self.bounds_check(enforce=False)) :
            message += f" {m}"

        return message

    def set_maximum(self, quantity):
        self.maximum = quantity
        return f"Set maximum of {self.name} to {self.maximum}."

    def set_minimum(self, quantity):
        self.minimum = quantity
        return f"Set minimum of {self.name} to {self.minimum}."

    def handle_command(self, context):
        command, args = self.parse_args(context)
        for c in self.commands:
            if command in c.names:
                return c.handle(args, context.character)

        return f"Command {command} not found."

    @staticmethod
    def from_json(data):
        return Tracker(**data)


class CoinTracker(Tracker):
    def __init__(self, name, default=0, quantity=0, reset_on_rest=False):
        super().__init__(
            name=name,
            default=default,
            quantity=quantity,
            reset_on_rest=reset_on_rest,
        )
        self.add_command_name("subtract", "spend")

    def handle_command(self, context):
        command, args = self.parse_args(context)

        scrubbed_args = []
        for arg in args:
            if (m := re.match(fr"(?P<qty>\d+){self.name}", arg)) :
                scrubbed_args.append(m.group("qty"))
            else:
                scrubbed_args.append(arg)

        for c in self.commands:
            if command in c.names:
                return c.handle(args, context.character)

        return f"Command {command} not found."

    @staticmethod
    def from_json(data):
        return CoinTracker(**data)


class HitDieTracker(Tracker):
    def __init__(self, name="hd", default=0, quantity=0, reset_on_rest=True):
        super().__init__(
            name=name,
            default=default,
            quantity=quantity,
            reset_on_rest=reset_on_rest,
        )
        self.add_command(TrackerCommand(["heal"], [], self.heal))

    def rest(self):
        if not self.reset_on_rest:
            return

    def heal(self):
        pass


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
            "type": self.__class__.__name__,
            "name": self.name,
            "quantity": {k: self.trackers[k].to_json() for k in self.trackers},
            "reset_on_rest": self.reset_on_rest,
        }

    @staticmethod
    def from_json(data):
        if "quantity" in data:
            data["quantity"] = collection_from_json(data["quantity"])
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
                kwargs["quantity"][c] = CoinTracker(c)
        super().__init__(name, kwargs.get("quantity"), False)

        self.set_regex()

    def set_regex(self):
        self.regex = re.compile(
            r"(?P<q>\d+)(?P<c>" + r"|".join(self.denoms) + r")",
            flags=re.IGNORECASE,
        )

    def parse_currency(self, args):
        try:
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
        except:
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

            self.trackers["ep"] = CoinTracker("ep")
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
            "electrum_enabled": "ep" in self.denoms,
        }

    @staticmethod
    def from_json(data):
        if "quantity" in data:
            trackers = data["quantity"]
            tracker_objects = {}

            # Handle old save files which don't use CoinTracker objects for
            # wealth by allowing user to update them to the new style
            # optionally.
            update_old_type = None
            for t in trackers:
                tracker_data = trackers[t]
                if tracker_data.get("type") == "Tracker":
                    if update_old_type is None:
                        update_old_type = cli.get_decision(
                            "Old save file uses less flexible classic trackers"
                            " rather than custom coin trackers for coin"
                            " collection. Update to new type?"
                        )

                    if update_old_type:
                        tracker_data["type"] = "CoinTracker"
                tracker_objects[t] = from_json(tracker_data)

            data["quantity"] = collections.OrderedDict(tracker_objects)
        return CoinCollection(**data)


class HealthCollection(TrackerCollection):
    def __init__(self, **kwargs):
        if kwargs.get("quantity") is None:
            kwargs["quantity"] = {
                "hp": Tracker(name="hp", reset_on_rest=True),
                "hd": Tracker(name="hd"),
            }

        super().__init__(
            name=kwargs.get("name", "health"),
            quantity=kwargs.get("quantity"),
            reset_on_rest=True,
        )


def from_json(data):
    try:
        tracker_type = data.pop("type")
    except KeyError:
        tracker_type = "Tracker"

    return globals()[tracker_type].from_json(data)


def collection_from_json(data):
    return {t: from_json(data[t]) for t in data}


def stringify_tracker_iterable(trackers, heading="Trackers", indent=1):
    tracker_string = "\n" + "\n".join([t.to_string(indent) for t in trackers])
    return f"{heading}:{tracker_string}"


def print_tracker_iterable(trackers):
    print(f"\n{stringify_tracker_iterable(trackers)}\n")


tracker_collection_presets = {
    "coins": lambda: CoinCollection("coins"),
    "wealth": lambda: CoinCollection("wealth"),
}
