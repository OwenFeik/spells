class Tracker():
    def __init__(self, name, default = 0, quantity = None):
        self.name = name
        self.quantity = quantity if quantity is not None else default
        self.default = default

    def __str__(self):
        return f'{self.name}: {self.quantity}'

    def handle_command(self, arguments):
        command, *args = arguments

        if command == 'reset':
            self.quantity = self.default
            return f'Reset {self.name} to {self.quantity}.'
        elif command == '++':
            self.quantity += 1
            return f'Incremented {self.name}. Current value: {self.quantity}'
        elif command == '--':
            self.quantity -= 1
            return f'Decremented {self.name}. Current value: {self.quantity}'
        elif not args:
            return f'If command {command} exists, it requires arguments.'

        if args[0].isnumeric():
            quantity = int(args[0])

        if command in ['add', 'give', '+', '+=']:
            self.quantity += quantity
            return f'Added {quantity} to {self.name}. Current value: {self.quantity}.'
        elif command in ['subtract', 'take', '-', '-=']:
            self.quantity -= quantity
            return f'Subtracted {quantity} from {self.name}. Current value: {self.quantity}.'
        elif command in ['set', '=']:
            self.quantity = quantity 
            return f'Set {self.name} to {self.quantity}.'
        else:
            return f'Command {command} not found.'

    def to_json(self):
        return {
            'name': self.name,
            'quantity': self.quantity,
            'default': self.default
        }

    @staticmethod
    def from_json(data):
        return Tracker(**data)
