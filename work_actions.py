from utils import delay, dotdotdot
import random as rnd

from obj_dict import ObjDict  # DELETE LATER

type objUID = str

class WorkActions:

    ## DELETE LATER ##
    # add the [] syntax notation like dictionary
    # e.g. Class["variables"] works as Class.variables
    # def __setitem__(self, key, value):
    #     setattr(self, key, value)
    # def __getitem__(self, key):
    #     return getattr(self, key)
    # def load_object_dictionary(self, obj_dict: ObjDict) -> None:
    #     self.O = obj_dict
    # def load_events_data_structure(self, dict):
    #     for k, v in dict.items():
    #         self[k] = v
    ##################
    
    def __init__(self):
        self.email_gen = None

    def email_work(self, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if room == "offices":
            if do_print:
                print("Logging into computer to check emails/work.........\n")

            # Initialize the generator only once
            
            if self.email_gen is None:
                self.email_gen = self.email_generator()

            try:

                """
                if character != "player":
                    random_input = rnd.choice([True, False])
                """

                email_message, email_score = next(self.email_gen)
                current_likeability = self.O.get_character_data(
                    "likability", character
                )

                if do_print: print(email_message)
                # for player and NPC
                if character == "player":
                    user_input = (
                        input(
                            "Do you want to forward this email to the boss? (y/n): "
                        )
                        .strip()
                        .lower()
                    )
                    print("")
                else:
                    user_input = rnd.choice(["y", "n"])

                if user_input == "y":
                    self.O.set_character_data(
                        character, "likability", current_likeability + email_score
                    )
                    if do_print: 
                        print("Email forwarded to the boss.")
                        delay()
                        dotdotdot()

                    if do_print:
                        if email_score > 0:
                            print(
                                "The boss thanks you for bringing this to his attention."
                            )
                        else:
                            print("The boss thinks this email is wasting his time.")
                    print(f"Impact on likability: {email_score}\n")
                else:
                    if do_print:
                        if user_input == "n":
                            print("You chose not to forward the email.\n")
                            dotdotdot()
                        else:
                            print(
                                "Invalid input. Email not forwarded. Should have put a proper input.\n"
                            )
                            dotdotdot()
                    if email_score > 0:
                        self.O.set_character_data(
                            character,
                            "likability",
                            current_likeability - email_score,
                        )
                        if do_print:
                            print("You failed at doing a simple job and the boss is disappointed that you exist.")
                        print(f"Impact on likability: -{email_score}\n")
                    else:
                        print("Sometimes no news is good news! Impact on likability: 2\n")

                        self.O.set_character_data(
                            character, "likability", current_likeability + 2
                        )
                self.O.set_character_data(character, "skip_turn", 2)
                self.O.set_character_data(character, "skip_cause", "you are doing work")
                return True

                # print(self.O.get_character_data("likability", character))

            except StopIteration:
                if do_print:
                    print("No more emails to read.")
                self.email_gen = None

            return True
        if do_print:
            print("You need to go to the offices to do this")
        return False

    # Generator to yield one email at a time
    def email_generator(self):
        for email, score in self["email_minigame"].items():
            yield email, score

    def talk_to(
        self, to_character: objUID, from_character: objUID, do_print=True
    ) -> bool:
        to_character = self.map_to_actual_obj(
            to_character, from_character
        )  # e.g. maps Philip to NPC_1
        room = self.O.get_holder(from_character)
        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print:
                print(
                    f"You cannot talk to a {to_character}, this is an object, you can say something else"
                )
            return False
        to_char_name = self.O.get_character_data("name", to_character)
        if to_character in self.O.get_holding(room):  # the character same room as you
            if to_character == "secretary":
                pass  # say something, maybe randomized
            if to_character == "boss":
                # say something and the boss scootches over
                is_boss_anniversary = self["variables"]["is_boss_anniversary"]

                if is_boss_anniversary:
                    if do_print:
                        print("THANK YOU FOR COMING TO MY PARTY!")
                        delay()
                        print("I'M SO HAPPY TO HAVE YOU ALL HERE!")
                        delay()
                        print("I'M SO GRATEFUL FOR ALL OF YOU!")
                        delay()
                        print("DO YOU KNOW WHAT WILL MAKE THIS PARTY EVEN")
                        delay()
                        print("BETTER? PLENTY OF OVERTIME WORK! AND CAKE!")
                        print()
                else:   
                    if do_print:
                        print("I don't want to talk to you, I'm busy!")

                    adjacent_room = self.O.find_next_room(
                        rnd.choice(["N", "S", "E", "W"]), room
                    )
                    while adjacent_room == None:
                        adjacent_room = self.O.find_next_room(
                            rnd.choice(["N", "S", "E", "W"]), room
                        )

                    self.O.change_holder(to_character, room, adjacent_room)

            # Talk to NPC
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
                    if do_print:
                        print(dialogues[current_index])

                    # Update the pointer to the next dialogue, looping back to the start if necessary
                    self.dialogue_pointers[to_character] = (current_index + 1) % len(
                        dialogues
                    )
                    return True
                else:
                    if do_print:
                        print("Silence..... they have nothing else to say to you")
                    return False

        else:  # character not in the ROOM
            if do_print:
                print(f"go find {to_char_name} or say something else")
        return True

    def give_obj(
        self, obj: objUID, to_character: objUID, from_character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(from_character)
        to_character = self.map_to_actual_obj(to_character, from_character)
        obj = self.map_to_actual_obj(obj, from_character)
        speaker_inventory = self.O.get_holding(from_character)

        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print:
                print(f"You cannot give to a {to_character}")
            return False
        gifted_name = self.O.get_character_data("name", to_character)
        current_friendliness = self.O.get_character_data("friendliness", to_character)
        if obj in speaker_inventory:

            if (
                self["variables"]["is_lights_out"]
                and "flashlight" not in speaker_inventory
            ):
                if do_print:
                    print("you cannot see anything let alone give an item to anyone")
                return False

            if to_character in self.O.get_holding(room):

                # for hacking script and translating the old intern notes
                if gifted_name == "Mr.Boss" and obj == "suspicious_document":
                    if do_print:
                        print("Well, well... you found it I knew I should have burnt as a sacrifice. Gotta hand it to you, kid you are sharp. Lucky for me, you did not run to those heathen board memebers or the cops. That is loyalty I can respect.\nTell you what keep this between us, and you can marry my daughter. She's been talking about you anyway. Plus, I could use a smart son-in-law to keep things... discree!")
                    self["variables"]["is_a_secret_endings"]["marry_daughter"] = True
                    return True


                    return True
                if gifted_name == "Steve Jobs":
                    if obj == "intern_coin":
                        if len(speaker_inventory) < self["variables"]["MAX_INVENTORY"]:
                            self.O.remove_holding(obj, from_character)
                            self.O.set_character_data(
                                to_character, "friendliness", current_friendliness + 5
                            )
                            if obj == "intern_coin":
                                if do_print:
                                    print("Here's the USB hacking script as promised.")
                                self.O.add_holding("usb_hacking_script", from_character)
                                return True
                        else:
                            if do_print:
                                print(
                                    "Classic Intern holding more stuff then you can use, try dropping some stuff if you really want this "
                                )
                            return False
                    elif obj == "old_intern_notes":
                        if do_print:
                            print("I see you need a genius to translate this for you. Wait one second", end="")
                            dotdotdot()
                            print("\nThe Text says: \nRule #1: Keep your desk clean. Apparently, the boss thinks clutter is a personal attack on his soul. Might be allergic to productivity too.\nRule #2: Always bring a flashlight to work. The lights go out sometimes and people just... disappear. Not saying it's haunted, but I'm not 'not' saying that either.\nRule #3 Make the boss happy. Even if it means pretending you care about his endless speeches. Nodding a lot helps.\nRule #4: Do some actual work. Apparently, staring intently at an empty spreadsheet does not count as “being productive.” Who knew?\nWeird tip: The secretary loves flowers... but I can not figure out which ones. Could just be stress gardening. Who knows.\nWeird tip: The secretary loves flowers... but I can not figure out which ones. Saw her fussing over some roses once. Could be nothing... or everything.\nHot Investment Tip: Buy Intern Coin. It is going to the moon! Trust me, I am basically a financial genius. Plus it is endorsed by our IT guy Steve Jobs.\nAlso by the way there is this suspicious safe in the boss's office... been wondering what is inside. Have not found out what was inside in my time here probably just old mementos.\n ")
                            dotdotdot()
                            print("I liked that Intern shame 'THEY' got him")

                        
                        return True
                    
                    elif obj == "suspicious_document":
                        if do_print:
                            print("What is this??? Susicious documents with dirt against the Boss!! Good job my boy with this I can finally be free!!")
                        # switch the ending on and gets checked after turns
                        self["variables"]["is_a_secret_endings"]["become_boss"] = True
                        return True

                    else:
                        if do_print:
                            print(
                                "What is this? Worldy goods are useless to me the only thing I treasure crypto currency."
                            )
                        return False

                # for the hint to the safe

                if gifted_name == "Morgana":
                    if obj == "blue_flower":
                        self.O.remove_holding(obj, from_character)
                        self.O.set_character_data(
                            to_character, "friendliness", current_friendliness + 5
                        )
                        if do_print:
                            print(
                                "Thank you so much!! This is perfect for my desk. In exchange I will give you a suggestion for dealing with the Boss. When ever he is anrgy he fratincally spells his dogs name L-U-C-Y outloud in his office for some reason. At that time best not to be to close."
                            )  # INPUT HINT here
                        return True
                    else:
                        if do_print:
                            print(
                                "Sorry my desk is over flowing as is, I do not need more stuff. But I would like something to liven the place up."
                            )
                        return False

                # Everyone else
                if do_print:
                    print(f"{gifted_name}: Thanks! You're the best!")
                    print(f"Friendliness with {gifted_name} increased")
                self.O.remove_holding(obj, from_character)
                self.O.add_holding(obj, to_character)
                if self.O.get_character_data("uses_parser", from_character):
                    self.O.set_character_data(
                        to_character, "friendliness", current_friendliness + 1
                    )
                return True
            else:
                if do_print:
                    print(f"Go look for {gifted_name}")
        else:
            if do_print:
                print(f"You don't have {obj}")
        return False
