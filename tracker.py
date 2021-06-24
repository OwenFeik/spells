import collections
import enum
import re

import roll

import cli
import constants
import utilities


class AbstractTracker:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.default = kwargs.get("default")
        self.quantity = kwargs.get("quantity")
        self.reset_on_rest = kwargs.get("reset_on_rest", False)
        self.commands = self.create_default_commands()

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
            command == self.name or re.match(rf"[\w\.]+\.{self.name}", command)
        ):
            command, *args = args
            command = command.lower()

        return command, args

    def create_default_commands(self):
        return []

    def handle_command(self, context):
        command, args = self.parse_args(context)
        for c in self.commands:
            if command in c.names:
                return c.handle(args, context)

        return f"Command {command} not found."

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

    def get_command_names(self, name):
        for c in self.commands:
            if name in c.names:
                return c.names

    def remove_command(self, name):
        remove = []
        for c in self.commands:
            if name in c.names:
                remove.append(c)

        for c in remove:
            self.commands.remove(c)

    def replace_command(self, command):
        self.remove_command(command.name)
        self.add_command(command)

    def reset(self):
        if self.default is not None:
            self.quantity = self.default

    def rest(self):
        if self.reset_on_rest:
            self.reset()

    def level_up(self, character, level):
        return None

    def add_to_char(self, char):
        char.trackers.add_tracker(self)

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
    STRING = enum.auto()  # require a string as an argument
    TRACKER = enum.auto()  # require a tracker as an argument
    OPTIONAL = enum.auto()  # make argument optional
    CHARACTER = enum.auto()  # require the active character as an argument
    ALLOW_EQUALS = enum.auto()  # allow format "command = argument"


class TrackerCommand:
    MISSING_ARG_MESSAGE = "This command requires an argument."

    def __init__(self, names, options, func):
        self.names = names
        self.needs_string = TrackerCommandOptions.STRING in options
        self.needs_quantity = TrackerCommandOptions.QUANTITY in options
        self.needs_tracker = TrackerCommandOptions.TRACKER in options
        self.needs_character = TrackerCommandOptions.CHARACTER in options
        self.arg_optional = TrackerCommandOptions.OPTIONAL in options
        self.arg_allow_equals = TrackerCommandOptions.ALLOW_EQUALS in options
        self.func = func

    @property
    def name(self):
        return self.names[0] if self.names else None

    @property
    def needs_arg(self):
        return self.needs_string or self.needs_quantity

    def call(self, quantity=None, string=None, character=None, tracker=None):
        args = ()

        if self.needs_quantity:
            args = args + (quantity,)
        if self.needs_string:
            args = args + (string,)
        if self.needs_tracker:
            args = args + (tracker,)
        if self.needs_character:
            args = args + (character,)

        return self.func(*args)

    def handle(self, args, context):
        quantity = string = tracker = None
        character = context.character
        if not args:
            if not self.needs_arg or self.arg_optional:
                return self.call(
                    quantity=quantity,
                    string=string,
                    tracker=tracker,
                    character=character,
                )
            else:
                return TrackerCommand.MISSING_ARG_MESSAGE

        if self.needs_string:
            string = args[0]
        elif args[0].isnumeric():
            quantity = int(args[0])
        elif self.needs_tracker:
            tracker = context.get_tracker(args[0])
        elif (
            self.arg_allow_equals
            and len(args) >= 2
            and args[0] == "="
            and args[1].isnumeric()
        ):
            quantity = int(args[1])
        elif (rolls := roll.get_rolls(" ".join(args), max_qty=1)) :
            quantity = rolls[0].total
        else:
            return TrackerCommand.MISSING_ARG_MESSAGE

        return self.call(
            quantity=quantity,
            string=string,
            tracker=tracker,
            character=character,
        )


class Tracker(AbstractTracker):
    def __init__(self, **kwargs):
        kwargs["quantity"] = kwargs.get("quantity", 0)
        super().__init__(**kwargs)
        self.maximum = kwargs.get("maximum")
        self.minimum = kwargs.get("minimum")
        self.commands = self.create_default_commands()
        self._old_quantities = []  # stack

    def __repr__(self):
        return super().__repr__().replace("Abstract", "", 1)

    @property
    def at_max(self):
        if self.maximum is None:
            return False
        return self.quantity >= self.maximum

    @property
    def at_min(self):
        if self.minimum is None:
            return False
        return self.quantity <= self.minimum

    def create_default_commands(self):
        return [
            TrackerCommand(["reset"], [], self.reset),
            TrackerCommand(["rest"], [], self.toggle_rest_behaviour),
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
                self.remove,
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
                    TrackerCommandOptions.OPTIONAL,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_minimum,
            ),
            TrackerCommand(
                ["max", "maximum"],
                [
                    TrackerCommandOptions.QUANTITY,
                    TrackerCommandOptions.OPTIONAL,
                    TrackerCommandOptions.ALLOW_EQUALS,
                ],
                self.set_maximum,
            ),
            TrackerCommand(
                ["unset"], [TrackerCommandOptions.STRING], self.unset
            ),
        ]

    def start_delta(self):
        self._old_quantities.append(self.quantity)

    def finish_delta(self, as_string=False):
        delta = 0
        if self._old_quantities:
            delta = self.quantity - self._old_quantities.pop()

        if as_string:
            if delta:
                return f" ({'+' if delta > 0 else ''}{delta})"
            else:
                return ""
        else:
            return delta

    def reset(self):
        if self.default is not None:
            self.start_delta()
            super().reset()
            return (
                f"Reset {self.name} to {self.quantity}"
                f"{self.finish_delta(True)}."
            )
        else:
            return f"{self.name} has no default to reset to."

    def rest(self):
        if self.reset_on_rest:
            return self.reset()

    def bounds_check(self, enforce=True, value=None):
        if value is None:
            value = self.quantity
        else:
            enforce = False

        if self.maximum is not None and value > self.maximum:
            if enforce:
                self.start_delta()
                self.quantity = self.maximum
                delta = self.finish_delta()

                message = f"Now at maximum: {self.maximum}."
                if delta:
                    message += f" Lost {abs(delta)} to overflow."
                return message
            else:
                return f"Warning: over maximum of {self.maximum}."
        elif self.minimum is not None and value < self.minimum:
            if enforce:
                self.start_delta()
                self.quantity = self.minimum
                delta = self.finish_delta()
                message = f"Now at minimum: {self.minimum}."
                if delta:
                    message += f" Lost {delta} to underflow."
                return message
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

        return message

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
        self.start_delta()
        self.quantity = quantity
        message = f"Set {self.name} to {quantity}{self.finish_delta(True)}."

        if (m := self.bounds_check(enforce=False)) :
            message += f" {m}"

        return message

    def set_maximum(self, quantity=None):
        if quantity is not None:
            self.maximum = quantity
            return f"Set maximum of {self.name} to {self.maximum}."
        else:
            return f"Current maximum of {self.name}: {self.maximum}."

    def set_minimum(self, quantity=None):
        if quantity is not None:
            self.minimum = quantity
            return f"Set minimum of {self.name} to {self.minimum}."
        else:
            return f"Current minimum of {self.name}: {self.minimum}."

    def unset(self, name):
        UNSETTABLE = ["default", "maximum", "minimum"]

        command_names = self.get_command_names(name)
        if command_names is None:
            return (
                "Only "
                + ", ".join(UNSETTABLE[:-1])
                + f" and {UNSETTABLE[-1]} can be unset."
            )

        for n in command_names:
            if n in UNSETTABLE:
                setattr(self, n, None)
                return f"Removed {n} for {self.name}."
        return f"{name} cannot be unset."

    def to_json(self):
        return {
            **super().to_json(),
            "maximum": self.maximum,
            "minimum": self.minimum,
        }

    @staticmethod
    def from_json(data):
        return Tracker(**data)


class TrackerCollection(AbstractTracker):
    TRACKER_ACCESS_OPERATOR = "."

    def __init__(self, **kwargs):
        if kwargs.get("quantity") is None:
            kwargs["quantity"] = {}
        if kwargs.get("default") is None:
            kwargs["default"] = {}

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<TrackerCollection name={self.name} trackers={self.quantity}>"

    @property
    def trackers(self):
        return self.quantity

    def create_default_commands(self):
        return [
            TrackerCommand(
                ["add"],
                [
                    TrackerCommandOptions.TRACKER,
                    TrackerCommandOptions.CHARACTER,
                ],
                self.add_from_other,
            ),
            TrackerCommand(
                ["remove"],
                [
                    TrackerCommandOptions.TRACKER,
                    TrackerCommandOptions.CHARACTER,
                ],
                self.move_to_root,
            ),
        ]

    def get(self, name=None, names=None):
        if not names and name:
            names = TrackerCollection.expand_name(name)

        if not names:
            return None

        if (t := self.trackers.get(names[0])) :
            if len(names) == 1:
                return t
            elif isinstance(t, TrackerCollection):
                return t.get(names=names[1:])

        return None

    def get_parent(self, tracker):
        if isinstance(tracker, str):  # allow name
            names = TrackerCollection.expand_name(tracker)[:-1]
            if len(names) == 0:
                return self
            return self.get(names=names)
        elif isinstance(tracker, AbstractTracker):  # or Tracker object
            to_visit = [self]
            while to_visit:
                tc = to_visit.pop(0)
                for t in tc.trackers.values():
                    if t is tracker:
                        return tc
                    elif isinstance(t, TrackerCollection):
                        to_visit.append(t)
        return None

    def rest(self):
        messages = []
        for t in self.trackers.values():
            if isinstance((m := t.rest()), list):
                messages.extend(m)
            elif isinstance(m, str):
                messages.append(m)

        return messages

    def level_up(self, character, level):
        message = ""
        for t in self.trackers.values():
            if (m := t.level_up(character, level)) :
                message += "\n" + m

        if message:
            return message[1:]
        return None

    def add_to_char(self, char):
        char.trackers.add_tracker(self)

    def add_from_other(self, tracker, character):
        parent = character.trackers.get_parent(tracker)
        parent.delete_child(tracker.name)
        self.add_tracker(tracker)
        return f"Added {tracker.name} to {self.name}."

    def add_tracker(self, child):
        self.trackers[child.name] = child

    def move_to_root(self, tracker, character):
        if tracker.name in self.trackers:
            self.delete_child(tracker.name)
            character.trackers.add_tracker(tracker)
            return f"Removed {tracker.name} from {self.name}."
        else:
            return f"{tracker.name} isn't in {self.name}."

    def delete_child(self, name):
        del self.trackers[name]

    def to_string(self, indent=0):
        return "\t" * indent + stringify_tracker_iterable(
            self.trackers.values(), self.name, indent + 1
        )

    def get_child(self, name):
        return self.trackers.get(name)

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

    @staticmethod
    def expand_name(name):
        return name.split(TrackerCollection.TRACKER_ACCESS_OPERATOR)

    @staticmethod
    def get_root_name(name):
        return TrackerCollection.expand_name(name)[0]

    @staticmethod
    def get_leaf_name(name):
        return TrackerCollection.expand_name(name)[-1]


class CoinTracker(Tracker):
    def __init__(self, **kwargs):
        kwargs["minimum"] = kwargs.get("minimum", 0)
        super().__init__(**kwargs)
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
                return c.handle(args, context)

        return f"Command {command} not found."

    @staticmethod
    def from_json(data):
        return CoinTracker(**data)


class CoinCollection(TrackerCollection):
    DENOMINATIONS = ["cp", "sp", "ep", "gp", "pp"]
    DENOMINATION_MAPPING = {
        "cp": 1,
        "sp": 10,
        "ep": 50,
        "gp": 100,
        "pp": 1000,
    }

    def __init__(self, **kwargs):
        self.denoms = CoinCollection.DENOMINATIONS[:]
        if not kwargs.get("electrum_enabled"):
            self.denoms.remove("ep")

        if kwargs.get("quantity") is None:
            kwargs["quantity"] = collections.OrderedDict()
            for c in self.denoms:
                kwargs["quantity"][c] = CoinTracker(name=c)

        kwargs["reset_on_rest"] = False
        super().__init__(**kwargs)

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

            self.trackers["ep"] = CoinTracker(name="ep")
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
        else:
            return f"Command {command} does not exist."

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


class HitDieTracker(Tracker):
    def __init__(self, hp_tracker, **kwargs):
        for kw, arg in [
            ("minimum", 0),
            ("maximum", 0),
            ("reset_on_rest", False),
        ]:
            kwargs[kw] = kwargs.get(kw, arg)

        super().__init__(**kwargs)
        self.add_command(
            TrackerCommand(
                ["heal"], [TrackerCommandOptions.CHARACTER], self.heal
            )
        )
        self.hp = hp_tracker
        self.die_size = kwargs.get("die_size")

    def heal(self, character):
        if self.hp.maximum is None:
            if cli.get_decision(
                f"{character.name} doesn't have maximum hit points set."
                " Set now?"
            ):
                max_hp = cli.get_integer("Max hit points")
                self.hp.set_maximum(max_hp)
                self.hp.set_default(max_hp)
            else:
                return

        if character.stats:
            mod = character.stats.get_mod("con")
        else:
            mod = cli.get_integer(
                f"{character.name} doesn't have stats."
                " What is their constitution modifier?"
            )

        self.start_delta()
        self.hp.start_delta()
        while self.quantity and self.hp.quantity < self.hp.maximum:
            self.quantity -= 1
            self.hp.add(roll.get_rolls(f"d{self.die_size} + {mod}")[0].total)

        return (
            f"Used {abs(self.finish_delta())} {self.name} to heal for"
            f" {self.hp.finish_delta()} hit points. Now at {self.hp.quantity}"
            " hit points."
        )

    def to_json(self):
        return {**super().to_json(), "die_size": self.die_size}

    @staticmethod
    def from_json():
        raise TypeError(
            "Hit die tracker cannot be instantiated without health tracker."
        )


class HitDieCollection(TrackerCollection):
    def __init__(self, hp_tracker, **kwargs):
        kwargs["reset_on_rest"] = kwargs.get("reset_on_rest", True)

        super().__init__(**kwargs)
        self.hp_tracker = hp_tracker
        self.character_level = kwargs.get("character_level")

        self.add_command(
            TrackerCommand("heal", [TrackerCommandOptions.CHARACTER], self.heal)
        )

    def ordered_trackers(self):
        return sorted(self.trackers.values(), key=lambda t: -t.die_size)

    def start_mutation(self):
        self.hp_tracker.start_delta()
        trackers = self.ordered_trackers()
        [t.start_delta() for t in trackers]
        return trackers

    def finish_mutation(self, trackers=None):
        trackers = trackers if trackers else self.ordered_trackers()
        return utilities.punctuate_list(
            [f"{abs(d)}{t.name}" for t in trackers if (d := t.finish_delta())]
        )

    def heal(self, character):
        if self.hp_tracker.at_max:
            return f"{character.name} is already at full health."

        trackers = self.start_mutation()

        i = 0
        while i < len(trackers) and not self.hp_tracker.at_max:
            if trackers[i].at_min:
                i += 1
            else:
                trackers[i].heal(character)

        if (m := self.finish_mutation(trackers)) :
            return (
                f"Spent {m}, regaining {self.hp_tracker.finish_delta()} hit"
                f" points to {self.hp_tracker.quantity}."
            )
        else:
            return "No hit die to expend."

    def rest(self):
        trackers = self.start_mutation()

        i = 0
        while i < len(trackers) and trackers[i].at_max:
            i += 1

        to_regain = max(self.character_level // 2, 1)
        while i < len(trackers) and to_regain:
            trackers[i].add(1)
            to_regain -= 1

            while i < len(trackers) and trackers[i].at_max:
                i += 1

        if (m := self.finish_mutation(trackers)) :
            return f"Regained {m}."

    def get_tracker_from_die_size(self, size, create=True):
        name = f"d{size}"
        t = self.trackers.get(name)
        if t is None:
            t = HitDieTracker(self.hp_tracker, name=name, die_size=size)
            self.add_tracker(t)
        return t

    def set_up_hd(self, char):
        self.character_level = 0
        self.quantity = {}
        for k in char.klasses:
            size = HealthCollection.get_hit_die_size(k)
            t = self.get_tracker_from_die_size(size)
            t.maximum += k["level"]
            t.quantity = t.maximum

            self.character_level += k["level"]

    def level_up(self, character, level):
        t = self.get_tracker_from_die_size(
            HealthCollection.get_hit_die_size(level)
        )
        t.maximum += 1
        t.quantity += 1

    def to_json(self):
        return {
            **super().to_json(),
            "character_level": self.character_level,
        }


class HealthCollection(TrackerCollection):
    HIT_DIE_COLLECTION_NAME = "hd"
    HIT_POINTS_TRACKER_NAME = "hp"

    def __init__(self, **kwargs):
        kwargs["quantity"] = kwargs.get(
            "quantity", HealthCollection.default_quantity()
        )
        super().__init__(**kwargs)
        self.hp = self.trackers[HealthCollection.HIT_POINTS_TRACKER_NAME]
        self.hd = self.trackers[HealthCollection.HIT_DIE_COLLECTION_NAME]

        self.add_command(
            TrackerCommand(
                ["heal"], [TrackerCommandOptions.CHARACTER], self.hd.heal
            )
        )
        self._set_up_done = kwargs.get("set_up_done", False)

    def add_to_char(self, char):
        if not self._set_up_done:
            self.hd.set_up_hd(char)

            if cli.get_decision(
                "Enter maximum hit points?"
                " Otherwise average will be calculated."
            ):
                self.hp.quantity = self.hp.maximum = cli.get_integer(
                    "Maximum hit points"
                )
            else:
                first = True
                quantity = 0
                for k in char.klasses:
                    levels = k["level"]
                    size = HealthCollection.get_hit_die_size(k)
                    if first:
                        levels -= 1
                        quantity += size
                        first = False
                    quantity += (
                        HealthCollection.get_hit_die_average(size) * levels
                    )
                    quantity += char.stats.get_mod("con") * k["level"]

                self.hp.quantity = self.hp.maximum = quantity

            self._set_up_done = True
        super().add_to_char(char)

    def level_up(self, character, level):
        message = super().level_up(character, level)

        size = HealthCollection.get_hit_die_size(level)
        if cli.get_decision("Roll for hit point increase?"):
            while (increase := roll.get_rolls(f"d{size}")[0].result) == 1:
                pass
        else:
            increase = HealthCollection.get_hit_die_average(size)
        increase += character.stats.get_mod("con")
        self.hp.maximum += increase

        m = f"Maximum hit points increased by {increase}."

        if message:
            return f"{message}\n{m}"
        else:
            return m

    @staticmethod
    def get_hit_die_average(size):
        return size // 2 + 1

    @staticmethod
    def get_hit_die_size(klasse):
        size = klasse.get("hit_die")
        if size is None:
            size = constants.KLASSE_HIT_DIE.get(
                klasse["name"],
                cli.get_choice(
                    f"Which hit die does the class {klasse['name']} use?",
                    [f"d{s}" for s in constants.HIT_DIE_SIZES],
                    constants.HIT_DIE_SIZES,
                ),
            )
            klasse["hit_die"] = size
        return size

    @staticmethod
    def default_quantity():
        hp = Tracker(
            name=HealthCollection.HIT_POINTS_TRACKER_NAME,
            reset_on_rest=True,
        )
        return {
            HealthCollection.HIT_POINTS_TRACKER_NAME: hp,
            HealthCollection.HIT_DIE_COLLECTION_NAME: HitDieCollection(
                hp, name=HealthCollection.HIT_DIE_COLLECTION_NAME
            ),
        }

    @staticmethod
    def from_json(data):
        trackers = data["quantity"]
        hp = from_json(trackers[HealthCollection.HIT_POINTS_TRACKER_NAME])
        hd_data = trackers[HealthCollection.HIT_DIE_COLLECTION_NAME]
        hd_quantity = {
            t: HitDieTracker(hp, **hd_data["quantity"][t])
            for t in hd_data["quantity"]
        }
        hd_data["quantity"] = hd_quantity
        hd = HitDieCollection(hp, **hd_data)
        data["quantity"] = {
            HealthCollection.HIT_POINTS_TRACKER_NAME: hp,
            HealthCollection.HIT_DIE_COLLECTION_NAME: hd,
        }
        data["set_up_done"] = True

        return HealthCollection(**data)


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
    "coins": lambda: CoinCollection(name="coins"),
    "wealth": lambda: CoinCollection(name="wealth"),
    "health": lambda: HealthCollection(name="health"),
}
