from jan_game_base import Events
import random

type objUID = str  # just means objUID is type string

class Events_Expanded(Events):
    def __init__(self):
        super().__init__()
        self.email_gen = None  # Initialize the email generator

    def email_work(self, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if room == "offices":
            print("Logging into computer to check emails/work.........\n")
            
            # Initialize the generator only once
            if self.email_gen is None:
                self.email_gen = self.email_generator()

            try:
                # Get the next email from the generator
                email_message, email_score = next(self.email_gen)
                print(email_message)
                print(f"Impact on reputation: {email_score}\n")
            except StopIteration:
                print("No more emails to read.")
                self.email_gen = None  # Reset the generator once all emails are read
            
            return True
        print("You need to go to the offices to do this")
        return False

    # Generator to yield one email at a time
    def email_generator(self):
        for email, score in self["email_minigame"].items():
            yield email, score

    def talk_to(self, to_character:objUID, from_character:objUID, do_print=True) -> bool:
        to_character = self.map_to_actual_obj(to_character, from_character)  # e.g. maps Philip to NPC_1
        room = self.O.get_holder(from_character)
        to_char_name = self.O.get_character_data("name", to_character)
        if self.O.get_obj_type(to_character) != "character":
            if do_print: print(f"You cannot talk to a {to_character}, this is an object, you can say something else")
            return False
        if to_character in self.O.get_holding(room): # the character same room as you
            if to_character == "secretary":
                pass  # say something, maybe randomized
            if to_character == "boss":
                # say something and the boss scootches over
                if do_print: print("I don't want to talk to you, I'm busy! or other dialogues")
                adjacent_room = self.O.find_next_room(random.choice(["N","S","E","W"]))
                while adjacent_room == None:
                    adjacent_room = self.O.find_next_room(random.choice(["N","S","E","W"]))
                self.O.change_holder(to_character, room, adjacent_room)
        else:  # character not in the room
            if do_print: print(f"go find {to_char_name} or say something else")
        return True
    
    def drink_medicine(self, obj, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj in inventory:
            if do_print: print("I drink medicine now say something")
            self.O.remove_holding(obj)
            self.O.set_character_data(character, "turn_speed", 100)  # make healthy
            return True
        if do_print: print("You don't have item! or maybe say something else")
        return False


    # Here try to override inventory
    # def show_inventory(self, character: objUID, do_print=True) -> bool:
    #     pass
