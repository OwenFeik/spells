import re
import random

import roll

class AbstractTracker:
    def __init__(self, name, default=None, quantity=None, reset_on_rest=False):
        self.name = name
        self.default = default
        self.quantity = quantity
        self.reset_on_rest = reset_on_rest

    def __str__(self):
        return self.to_string()

    def parse_args(self, context):
        command, *args = context.args
        command = command.lower()
        
        if (
            context.command in ['t', 'tracker', 'tc', 'collection']
            and command == self.name
        ):
            command, *args = args

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
    def __init__(self, name, default=0, quantity=None, reset_on_rest=False):
        super().__init__(
            name,
            default,
            quantity if quantity is not None else default,
            reset_on_rest
        )

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
    def __init__(self, name, quantity=None, reset_on_rest=False):
        super().__init__(
            name,
            default={},
            quantity={} if quantity is None else quantity,
            reset_on_rest=reset_on_rest
        )
        self.trackers = self.quantity

    def handle_command(self, context):
        command, args = self.parse_args(context)

        name = args[0]
        if name not in context.character.trackers:
            if name not in self.trackers:
                return f"If command {command} exists, it requires a" \
                    " tracker as an argument."
            else:
                t = self.trackers[name]
        else:
            t = context.character.trackers[name]

        if command in ["add", "+", "+="]:
            self.trackers[t.name] = t
            del context.character.trackers[t.name]
            self.add_child_to_char(context.character, t)
        

    def rest(self):
        for t in self.trackers.values():
            t.rest()

    def add_child_to_char(self, char, child):
        char.trackers[f'{self.name}.{child.name}'] = child

    def add_to_char(self, char):
        char.trackers[self.name] = self
        for t in self.trackers.values():
            self.add_child_to_char(char, t)

    def to_string(self, indent=0):
        return "\t" * indent + stringify_tracker_iterable(
            self.trackers.values(),
            self.name,
            indent + 1
        )

    def to_json(self):
        return {
            "type": "TrackerCollection",
            "name": self.name,
            "quantity": {k: self.trackers[k].to_json() for k in self.trackers},
            "reset_on_rest": self.reset_on_rest
        }

    @staticmethod
    def from_json(data):
        return TrackerCollection(**data)

def from_json(data):
    try:
        tracker_type = data.pop('type')
    except KeyError:
        tracker_type = 'Tracker'
    
    return {
        'AbstractTracker': AbstractTracker,
        'Tracker': Tracker,
        'TrackerCollection': TrackerCollection
    }[tracker_type](**data)


def stringify_tracker_iterable(trackers, heading="Trackers", indent=1):
    tracker_string = "\n" + "\n".join([t.to_string(indent) for t in trackers]) 
    return f"{heading}:{tracker_string}"

def print_tracker_iterable(trackers):
    print(f"\n{stringify_tracker_iterable(trackers)}\n")
