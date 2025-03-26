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
            
            if to_character != "player":
            # Retrieve dialogues and initialize a pointer for the character if not already set
                dialogues = self.O.get_character_data("dialogue", to_character)
                if not hasattr(self, "dialogue_pointers"):
                    self.dialogue_pointers = {}
                if to_character not in self.dialogue_pointers:
                    self.dialogue_pointers[to_character] = 0

                if dialogues and len(dialogues) > 0:
                    # Get the current dialogue based on the pointer
                    current_index = self.dialogue_pointers[to_character]
                    if do_print: print(dialogues[current_index])

                    # Update the pointer to the next dialogue, looping back to the start if necessary
                    self.dialogue_pointers[to_character] = (current_index + 1) % len(dialogues)
                    return True
                else:
                    if do_print: print("Silence..... they have nothing else to say to you")
                    return False
            
            '''
            if self.O.get_character_data("name", to_character) == "Steve Jobs":
                friendliness = self.O.get_character_data("friendliness", to_character)
                if friendliness > 4:
                    if do_print: print("heres a intern coin")
                    if len(self.O.get_holding(from_character)) < self["variables"]["MAX_INVENTORY"]:
                        self.O.add_holding("intern_coin", from_character)
                else:
                    if do_print: print("Watch out for fishing emails")'
            ''' # will soft lock the NPC into giving intern coins


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
    
    def give_obj(self, obj:objUID, to_character:objUID, from_character:objUID, do_print=True) -> bool:
        room = self.O.get_holder(from_character)
        to_character = self.map_to_actual_obj(to_character, from_character)  # map_to_actual_obj() ia a bit of a misnomer, the second argument is just used to identify the room and self 
        obj = self.map_to_actual_obj(obj, from_character)
        
        # if self.O.get_obj_type(to_character) == "static" and self.O.get_static_data("name", to_character) == "Steve Jobs" and obj == "usb_hacking_script": # and give item hacking script
        #     current_friendliness = self.O.get_static_data("friendliness", to_character)
        #     self.O.remove_holding(obj, from_character)
        #     self.O.set_static_data(to_character, "friendliness", current_friendliness+5)
        #     return True
        
        
        
        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print: print(f"You cannot give to a {to_character}")
            return False
        gifted_name = self.O.get_character_data("name", to_character)
        current_friendliness = self.O.get_character_data("friendliness", to_character)
        if obj in self.O.get_holding(from_character):
            if to_character in self.O.get_holding(room):

                #static chacarter Steve
                if gifted_name == "Steve Jobs": # and give item hacking script
                    if obj == "usb_hacking_script":
                        if len(self.O.get_holding(from_character)) < self["variables"]["MAX_INVENTORY"]:
                            self.O.remove_holding(obj, from_character)
                            self.O.set_character_data(to_character, "friendliness", current_friendliness+5)
                            if do_print: print("heres a intern coin")
                            self.O.add_holding("intern_coin", from_character)
                            return True 
                        else:
                            if do_print: print("Classic Intern holding more stuff then you can use, try dropping some stuff if you really want this device")
                            return False
                    else:
                        if do_print: print("What is this? Worldy goods are useless to me the only thing I treasure crypto currency.")
                        return False 
                     
                #Static chacarter Morgana
                if gifted_name == "Morgana": # and give item flower
                    if obj == "flower":
                        self.O.remove_holding(obj, from_character)
                        self.O.set_character_data(to_character, "friendliness", current_friendliness+5)
                        if do_print: print("Thank you so much!! This is perfect for my desk. In exchange I will give you a suggestion for dealing with the Boss. When ever he is anrgy he fratincally spells his dogs name L-U-C-Y outloud in his office for some reason. At that time best not to be to close.")#INPUT HINT here 
                        return True
                    else:
                        if do_print: print("Sorry my desk is over flowing as is, I do not need more stuff. But I would like something to liven the place up.")
                        return False


                #Everyone else
                if do_print:
                    print(f"{gifted_name}: Thanks! You're the best!")
                    print(f"Friendliness with {gifted_name} increased")
                self.O.remove_holding(obj, from_character)
                self.O.add_holding(obj, to_character)
                if self.O.get_character_data("uses_parser", from_character):
                    self.O.set_character_data(to_character, "friendliness", current_friendliness+1)
                return True
            else:
                if do_print: print(f"Go look for {gifted_name}")
        else:
            if do_print: print(f"You don't have {obj}")
        return False


    # Here try to override inventory
    # def show_inventory(self, character: objUID, do_print=True) -> bool:
    #     pass
