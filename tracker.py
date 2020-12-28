import re
import random

import roll


class Tracker:
    def __init__(self, name, default=0, quantity=None, reset_on_rest=False):
        self.name = name
        self.quantity = quantity if quantity is not None else default
        self.default = default
        self.reset_on_rest = reset_on_rest

    def __str__(self):
        return f"{self.name}: {self.quantity}"

    def handle_command(self, arguments):
        command, *args = arguments
        command = command.lower()

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

    def reset(self):
        self.quantity = self.default

    def rest(self):
        if self.reset_on_rest:
            self.reset()

    def to_json(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "default": self.default,
            "reset_on_rest": self.reset_on_rest,
        }

    @staticmethod
    def from_json(data):
        return Tracker(**data)
