from jan_game_base import Events
import random

type objUID = str  # just means objUID is type string

'''
class Events_Expanded(Events):
    def __init__(self):
        super().__init__()
        self.email_gen = None  # Initialize the email generator
        self.currency = {}  # Store currency for each character

    def check_balance(self, character: objUID, do_print=True):
        if character not in self.currency:
            self.currency[character] = 0

        if do_print:
            print(f"{character}'s current balance: ${self.currency[character]}")

        return self.currency[character]

    def freelance_work(self, character: objUID, do_print=True, skip_turns: int = 2):
        if character not in self.currency:
            self.currency[character] = 0

        self.O.set_character_data(character, "skip_turn", skip_turns)
        self.O.set_character_data(character, "skip_cause", "doing freelance work")

        earnings = 20
        self.currency[character] += earnings

        if do_print:
            print(f"{character} completed freelance work and earned ${earnings}. Current balance: ${self.currency[character]}")

        return True

    def earn_money_command(self, character: objUID, command: str, do_print=True):
        valid_commands = ["earn"]

        if command.lower() in valid_commands:
            self.freelance_work(character, do_print=do_print)
            return True

        if do_print:
            print("Invalid command. Try 'earn money' or 'do freelance'.")

        return False
'''
