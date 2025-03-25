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
            if do_print: 
                print("Logging into computer to check emails/work.........\n")
            
            # Initialize the generator only once
            if self.email_gen is None:
                self.email_gen = self.email_generator()

            try:
                # Get the next email from the generator
                email_message, email_score = next(self.email_gen)
                if do_print: 
                    print(email_message)
                    print(f"Impact on reputation: {email_score}\n")
            except StopIteration:
                if do_print: 
                    print("No more emails to read.")
                self.email_gen = None  # Reset the generator once all emails are read
            
            return True
        if do_print: 
            print("You need to go to the offices to do this")
        return False

    # Generator to yield one email at a time
    def email_generator(self):
        for email, score in self["email_minigame"].items():
            yield email, score

    def talk_to(self, to_character:objUID, from_character:objUID, do_print=True) -> bool:
        to_character = self.map_to_actual_obj(to_character, from_character)  # e.g. maps Philip to NPC_1
        room = self.O.get_holder(from_character)
        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print: print(f"You cannot talk to a {to_character}, this is an object, you can say something else")
            return False
        to_char_name = self.O.get_character_data("name", to_character)
        if to_character in self.O.get_holding(room): # the character same room as you
            if to_character == "secretary":
                pass  # say something, maybe randomized
            if to_character == "boss":
                # say something and the boss scootches over
                if do_print: print("I don't want to talk to you, I'm busy! or other dialogues")
                adjacent_room = self.O.find_next_room(random.choice(["N","S","E","W"]), room)
                while adjacent_room == None:
                    adjacent_room = self.O.find_next_room(random.choice(["N","S","E","W"]), room)
                self.O.change_holder(to_character, room, adjacent_room)
            if self.O.get_character_data("name", to_character) == "Steve Jobs":
                friendliness = self.O.get_character_data("friendliness", to_character)
                if friendliness > 4:
                    if do_print: print("heres a intern coin")
                    if len(self.O.get_holding(from_character)) < self["variables"]["MAX_INVENTORY"]:
                        self.O.add_holding("intern_coin", from_character)
                else:
                    if do_print: print("Watch out for fishing emails")


        else:  # character not in the ROOM
            if do_print: print(f"go find {to_char_name} or say something else")
        return True
    
    def drink_medicine(self, obj, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj in inventory:
            if self.O.get_character_data("turn_speed", character) < 100:
                if do_print: print("I drink medicine now say something")
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 100)  # make healthy
                return True
            else:
                if do_print: print("Why? You are perfectly healthy")
                return False            
        if do_print: print("You don't have item! or maybe say something else")
        return False


    # Here try to override inventory
    # def show_inventory(self, character: objUID, do_print=True) -> bool:
    #     pass
