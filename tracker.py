from utilities import parse_tracker_command

class Tracker():
    def __init__(self, quantity):
        self.quantity = quantity

    def handle_command(self, command):
        command, quantity = parse_tracker_command(command)

        if command == 'add':
            self.quantity += quantity
        elif command == 'subtract':
            self.quantity -= quantity 
