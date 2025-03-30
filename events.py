import random as rnd
import sys
import msvcrt

from time import sleep
from obj_dict import ObjDict

type objUID = str


class Events:
    """Class to modify the data structure"""

    def __init__(self):
        self.email_gen = None

    # add the [] syntax notation like dictionary
    # e.g. Class["variables"] works as Class.variables
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def load_object_dictionary(self, obj_dict: ObjDict) -> None:
        self.O = obj_dict

    def go_direction(self, dir: int, character: objUID, do_print=True) -> bool:
        """move to direction e.g. North, using character"""
        # override if you want to expand dialogues e.g. to say something else other than default "you cannot go there", you could say "that's the ladies room, you are not allowed there" if going north of washroom
        if (
            self.O.is_valid_obj(character)
            and self.O.get_obj_type(character) == "character"
        ):
            room = self.O.get_holder(character)
            dir_converted = self.direction(dir)[0]
            next_room = self.O.find_next_room(dir_converted, room)
            if next_room is not None:
                if next_room == "secret_room":
                    if "cabinet" in self.O.get_holding("boss_office"):
                        if do_print:
                            print("That way leads to nowhere")
                        return False
                    elif "key_card" not in self.O.get_holding(character):
                        if do_print:
                            print("you don't have keycard to access room")
                        return False
                    else:
                        if do_print:
                            print("FINALLY", end="")
                            self.symsymsym("!")
                self.O.change_holder(character, room, next_room)
                self.show_character_view(character, do_print, False)
                return True
            if do_print:
                print("That way leads to nowhere")
        return False

    def show_character_view(self, character: objUID, do_print=True, no_room_description=True) -> bool:
        """deduce the room the character is in and print what is there and valid directions of next rooms"""
        # override if you want to customize
        if not do_print:
            return True
        room = self.O.get_holder(character)
        # change to send_to_console if implementing formatter class
        print(room.upper())
        room_holdings = self.O.get_holding(room)
        room_holdings.remove(character)
        if self["variables"][
            "is_lights_out"
        ] and "flashlight" not in self.O.get_holding(character):
            if do_print:
                print("It's too dark, I cannot see anything")
                self.delay()
                print("Maybe a flashlight will help")  # or any light source later
            return False
        if not no_room_description:
            print(self.O.get_obj_description(room))
        if len(room_holdings) > 0:
            for n, item in enumerate(room_holdings):
                if self.O.get_obj_type(item) in ["character", "static_character"]:
                    room_holdings[n] = self.O.get_character_data("name", item)
            print(f"You can see ", end="")
            self.print_list(room_holdings)
        for i in ["N", "S", "E", "W"]:
            next_room = self.O.find_next_room(i, room)
            if next_room is not None:
                if next_room == "secret_room" and "cabinet" in self.O.get_holding(
                    "boss_office"
                ):
                    return True
                else:
                    print(f"to the {self.direction(i)} is {next_room}")
        return True

    def print_list(self, lst: list[str], add_newline=True) -> None:
        items_counting_duplicates = {}
        for n, item in enumerate(lst):
            if item == "poisoned_coffee":
                item = "coffee"  # to perceive as normal coffee
            item = item.replace("_", " ")
            if item not in items_counting_duplicates:
                items_counting_duplicates[item] = 1
            else:
                items_counting_duplicates[item] += 1
        for n,(item,count) in enumerate(items_counting_duplicates.items()):
            if count > 1:
                print(f"x{count} {item}", end="")
            else:
                print(item, end="")
            if n < len(items_counting_duplicates) - 1:
                if len(items_counting_duplicates) == 2:
                    print(" and ", end="")
                else:
                    print(", ", end="")
                    if n == len(items_counting_duplicates) - 2:
                        print("and ", end="")
            else:
                if add_newline:
                    print()

    def direction(self, dir: int | str):
        if dir in [1, "S"]:
            return "SOUTH"
        if dir in [2, "E"]:
            return "EAST"
        if dir in [3, "W"]:
            return "WEST"
        if dir in [0, "N"]:
            return "NORTH"

    def drop_obj(self, obj: objUID, character: objUID, do_print=True) -> bool:
        """check character holder (aka the room) and drop item there"""
        inventory = self.O.get_holding(character)

        # make coffee and poisoned coffee indistinguishable
        if obj == "coffee" and "poisoned_coffee" in inventory:
            obj = "poisoned_coffee"

        # maps obj synonym to actual object
        obj = self.map_to_actual_obj(obj, character)
        if obj == "no obj found":
            print(f"{obj} is not in the game dictionary")
            return False

        if self.O.is_valid_obj(obj) and obj in inventory:
            room = self.O.get_holder(character)
            self.O.change_holder(obj, character, room)
            if do_print:
                print("Done")
            return True
        return False

    def take_obj(self, obj: objUID, character: objUID, do_print=True) -> bool:
        """put obj1 to character holdings (aka inventory). also update holder"""
        room = self.O.get_holder(character)
        room_holdings_excluding_character = self.O.get_holding(room)
        room_holdings_excluding_character.remove(character)
        inventory = self.O.get_holding(character)

        # process synonyms aka manual check
        if obj == "coffee" and "poisoned_coffee" in room_holdings_excluding_character:
            obj = "poisoned_coffee"
        if obj == "cake":
            if self["variables"]["is_boss_anniversary"]:
                if do_print:
                    print("try again but put with the flavour")
                return False
            else:
                print("Ahh, you'll be in for a surprise in a few days")
                return True

        # map to actual object if there is
        obj = self.map_to_actual_obj(obj, character)
        if obj == "no obj found":
            print(f"{obj} is not in the game dictionary")
            return False
        


        if self.O.get_obj_type(obj) in ["character", "static_character"]:
            if do_print:
                print("You cannot pickup a living person! ", end="")
                self.delay()
                print("Unless", end="")
                self.dotdotdot()
                print("(the thoughts disappeared from your mind)")
            return False

        # "flashlight" in inventory is a placeholder, change to if holding any item with "illuminate" attribute later
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("You probed the surface until", end="")
                self.dotdotdot()
            # right side is percentage of giving up
            if rnd.randint(1, 100) <= 0:
                if do_print:
                    print("You gave up!")
                    print("Finding anything without lights is hard")
                    return True
            else:
                if len(room_holdings_excluding_character) > 0:
                    obj = rnd.choice(room_holdings_excluding_character)

                    # TODO: ability to carry (take) a character
                    # if asleep

                    # keep trying until its item, i.e. remove characters from choice
                    while self.O.get_obj_type(obj) in ["character", "static_character"]:
                        room_holdings_excluding_character.remove(obj)
                        if len(room_holdings_excluding_character) <= 0:
                            if do_print:
                                print("You search every corner of the room")
                                self.delay()
                                print("but unfortunately cannot find anything")
                            break
                        obj = rnd.choice(room_holdings_excluding_character)
                    else:
                        if do_print: print("You actually found an item!")
                        # falls through if its actually in the room
                else:
                    if do_print: 
                        print("until you probbed everywhere")
                        print("without any chance of finding anything")              

        if obj in room_holdings_excluding_character:
            #if heavy item no pick up
            if self.O.has_item_attribute("heavy", obj):
                if do_print:
                    print(f"{obj} is too heavy to pick up. Maybe hit the gym a little more?")
                return False
            if len(inventory) < self["variables"]["MAX_INVENTORY"]:
                if self["variables"]["is_boss_anniversary"]:
                    cake_list = ["strawberry_cake","vanilla_cake","chocolate_cake"]
                    if obj in cake_list:
                        cake_list.remove(obj)
                        for i,cake in enumerate(cake_list,1):
                            self.O.change_holder(cake, room, f"NPC_{i}")
                            # falls through to take the cake that was removed
                self.O.change_holder(obj, room, character)
                if do_print:
                    print("Done")
                return True
            else:
                if do_print:
                    print("You have too much stuff already")
        else:
            if not self["variables"]["is_lights_out"]:
                if do_print:
                    print(f"{obj} is not in the room!")
        return False

    def show_inventory(self, character: objUID, do_print=True) -> bool:
        if not do_print:
            return True
        inventory = self.O.get_holding(character)
        if len(inventory) > 0:
            print(f"You have with you ", end="")
            self.print_list(inventory)
        else:
            print("You aren't carrying anything.")
        return True

    def read_obj_description(
        self, obj: objUID, character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            obj = "poisoned_coffee"

        ## process synonyms here instead of the actual obj ##
        # check data.txt "other_valid_obj_name" section
        if obj == "inventory":
            self.show_inventory(character, do_print)

        # map the synonym to actual object here now
        obj = self.map_to_actual_obj(obj, character)
        if obj == "no obj found":
            print(f"{obj} is not in the game dictionary")
            return False

        # here obj was mapped to current room
        if obj == room:
            self.show_character_view(character, do_print, False)
            return True

        obj_inventory = self.O.get_holding(obj)
        obj_type = self.O.get_obj_type(obj)
        if not do_print and obj_type != "invalid object":
            # skips below "room" "character" and "item" prints
            return True

        # For the safe
        if room == "boss_office" and obj == "safe":
            if do_print:
                print(f"{obj}: ", end="")
                print(self.O.get_obj_description(obj))
                self.delay()
                print("It requires a 4 letter code to open. Do you wish to try? (y/n)")

                while True:
                    user_input = input("> ").strip().lower()
                    if user_input == "y":
                        print("You decided to try opening the safe.")
                        # Add logic for attempting to open the safe here
                        correct_code = "lucy"
                        attempts = 3

                        while attempts > 0:

                            code = input("Enter the 4 letter code: ").strip().lower()

                            if code == correct_code:
                                print("The safe opens and you find a keycard inside.")
                                self.O.add_holding("key_card", character)
                                return True
                            else:
                                attempts -= 1
                                if attempts > 0:
                                    print(
                                        "Incorrect code. You have",
                                        attempts - 1,
                                        "attempts left.",
                                    )
                                else:
                                    print(
                                        "You have run out of attempts. The safe is now locked. Try again later."
                                    )
                                    return False

                        return True
                    elif user_input == "n":
                        print("You decided not to try opening the safe.")
                        return True
                    else:
                        print(
                            "You stare at the safe. Perhaps you should make a decision."
                        )

            return True

        original_obj = obj
        if self["variables"]["is_lights_out"] and "flashlight" not in char_inventory:
            if self.O.get_obj_type(original_obj) in ["character", "static_character"]:
                if do_print:
                    print("You wailed you arms around the room")
                    print(f"looking for {original_obj} until", end="")
                    self.dotdotdot()
                for obj in set(room_holdings).difference([character]):
                    if self.O.get_obj_type(obj) in ["character", "static_character"]:
                        if do_print:
                            print("your hand landed somewhere unwanted")
                            print(
                                f'{self.O.get_character_data("name", obj)}: "Get your hands off me pervert!"'
                            )
                        return True
                # no character in the room
                print("You gave up")
                print("There must be no one in the room")
            else:
                print("You cannot examine anything in this darkness")
            return True
        obj = original_obj

        if obj_type == "room":
            print("Go there and find for yourself")
            return True

        # Get a description of the NPC Intern or Static Character
        if obj_type in ["character", "static_character"]:
            other_char_name = self.O.get_character_data("name", obj)
            if obj in room_holdings:
                print(self.O.get_obj_description(obj))
                if obj_type == "character":
                    print(f"likability: {self.O.get_character_data("likability", obj)}")
                    if len(obj_inventory) != 0:
                        print(f"{other_char_name} is holding ", end="")
                        self.print_list(obj_inventory)
                    else:
                        print(f"{other_char_name} isn't holding anything")
                return True
            else:
                print(f"{other_char_name} is in the {self.O.get_holder(obj)}")
                return True

        # item
        elif obj_type == "item":
            if obj in room_holdings or obj in char_inventory:  # objs_in_view:
                print(f"{obj}: ", end="")
                print(self.O.get_obj_description(obj))
                if self.O.has_item_attribute("container", obj):
                    objs_on_top = self.O.get_holding(obj)
                    number_objs_on_top = len(objs_on_top)
                    if number_objs_on_top >= 1:
                        print("on top also ", end="")
                        if number_objs_on_top > 1:
                            print("are ", end="")
                        elif number_objs_on_top == 1:
                            print("is ", end="")
                        self.print_list(objs_on_top)
                return True
            else:
                print("That isn't there!")
                return False
        return False

    def karateyd(
        self, verb: str, obj: objUID, character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        room_characterS = [
            o
            for o in room_holdings
            if self.O.get_obj_type(o) in ["character", "static_chracter"]
            and o != character
        ]
        if obj == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            obj = "poisoned_coffee"
        # either the valid obj name "room" or specified the actual room the character is in e.g. "cafeteria" can both be used
        if obj == "room" or obj == room:
            if do_print:
                print(f"you punched a wall in the {room}")
                self.dotdotdot(False)
                print("OUCH!")
                self.delay()
                print("That hurts.")
                self.delay()
                print("You came to your senses.")
                print("Im never punching a wall again.")
            return True
        map_obj_name = self.map_to_actual_obj(obj, character)
        if map_obj_name != "no obj found":
            obj = map_obj_name
        obj_type = self.O.get_obj_type(obj)

        original_obj = obj

        if self["variables"]["is_boss_anniversary"] and obj == "boss":
            if do_print:
                print("I LIKE HOW YOU HIT BOI!!!")
                self.delay()
                print("HERE'S MY DAUGHTER!")
            self["variables"]["is_a_secret_endings"]["marry_daughter"] = True
            return True

        if self["variables"]["is_lights_out"] and "flashlight" not in char_inventory:
            if obj != character:  # if you are not punching yourself
                obj_is_a_character = obj_type in ["character", "static_character"]
                if obj_is_a_character:
                    victim_name = self.O.get_character_data("name", original_obj)
                if obj not in char_inventory or obj_is_a_character:
                    if do_print:
                        print(
                            f"You {"fling your arm" if verb == "punch" else "ready your feet"} to try to {verb} {victim_name if obj_is_a_character else original_obj}",
                            end="",
                        )
                        self.dotdotdot()

                if obj_is_a_character:
                    if len(room_characterS) > 0:
                        obj = rnd.choice(room_characterS)
                        victim_name = self.O.get_character_data("name", obj)
                        if obj == original_obj:
                            if do_print:
                                print("and you actually hit your target!")
                        else:
                            if do_print:
                                print(
                                    f"but you hit {victim_name} instead!"
                                )  # somebody else
                        # falls through for character hit dialogue and item drop
                    else:
                        if do_print:
                            print("until you noticed there was actually no one there")
                            print(f"You've been {verb}ing air this whole time!")
                        return True

                elif obj not in char_inventory:
                    if do_print:
                        print(
                            f"Is {victim_name if obj_type in ["character","static_character"] else original_obj} even there?"
                        )
                        print("I can't really see anything")
                    return True

        if obj_type == "room":
            if do_print: print("go to that room to throw your tantrum")
            return False  # can't kick or throw tantrum in another room
        if obj_type == "item":
            if obj in room_holdings or obj in char_inventory:
                coffee_types = ["coffee", "poisoned_coffee"]
                if obj in coffee_types:
                    if do_print:
                        print("you broke the mug, ", end="")
                        self.delay()
                        print("hurt yourself, ", end="")
                        self.delay()
                        print("and spilled coffee", end="")
                        self.dotdotdot()
                        print("*good job*")
                        self.delay()
                    where_coffee_at = (
                        room
                        if any(item in room_holdings for item in coffee_types)
                        else (
                            character
                            if any(item in char_inventory for item in coffee_types)
                            else None
                        )
                    )
                    if where_coffee_at is not None:
                        self.O.remove_holding(obj, where_coffee_at)
                elif obj == "cabinet":
                    if do_print:
                        print("You punched the cabinet", end="")
                        self.dotdotdot()
                        print("and broke your fingers! ouch!")
                        self.delay()
                        print(
                            "But as the cabinet breaks into pieces you see something suspicious behind it"
                        )
                    self.O.add_holding("broken_cabinet", "boss_office")
                    self.O.remove_holding("cabinet", "boss_office")

                    return True

                else:
                    if do_print:
                        print("uhh", end="")
                        self.dotdotdot()
                        print("no thank you")
                        self.delay()
                return True
            else:
                if do_print:
                    print(
                        "You can't see that"
                    )  # --------------------------------------------------------------- maybe mistake
                return False
        if obj_type == "character":
            victim_name = self.O.get_character_data("name", obj)
            inventory = self.O.get_holding(obj)
            dropped_item = rnd.choice(inventory) if len(inventory) != 0 else None
            current_friendliness = self.O.get_character_data("friendliness", obj)

            if obj in self.O.get_holding(room):
                if do_print:
                    if obj == character:
                        print("Ughh, I hate myself!")
                        print("What is wrong with me!")
                        print(f"You {verb} yourself")
                        print(
                            f"You stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}"
                        )
                    else:
                        print(f"You {verb} {victim_name}", end="")
                        self.dotdotdot()

                        print(
                            f"{victim_name} stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}"
                        )
                        self.delay()
                        print(f'"shit man!"')
                        self.delay()
                        print(f"{victim_name} gets up, and brushes you off")
                        self.delay()
                        print(f"Friendliness with {victim_name} decreased")

                if dropped_item is not None:
                    self.O.change_holder(dropped_item, obj, room)
                    if (
                        self.O.get_character_data("uses_parser", character)
                        and obj != character
                    ):
                        self.O.set_character_data(
                            obj, "friendliness", current_friendliness - 1
                        )

                return True
            else:
                if do_print:
                    print(f"{victim_name} isn't even there dummy")
                return False

        if obj_type == "static_character" and obj in self.O.get_holding(room):
            victim_name = self.O.get_character_data("name", obj)
            if do_print:
                print(f"Im scared to {verb} {victim_name}, they might report me")

        return False

    def delay(self, speed_number=2) -> None:
        sys.stdout.flush()
        match speed_number:
            case 0:
                pass
            case 1:
                sleep(0.3)
            case 2:
                sleep(1.2)
            case 3:
                sleep(2.3)
            case 4:
                sleep(4)
            case 5:
                sleep(7)

    def symsymsym(self, symbol: str, newline=True) -> None:
        self.delay()
        for _ in range(3):
            print(f"{symbol}", end="")
            self.delay(1)
        if newline:
            print()

    def dotdotdot(self, newline=True) -> None:
        self.symsymsym(".", newline)

    def map_to_actual_obj(self, obj_synonym: objUID, character: objUID) -> objUID:

        # maps to actual object if given (well the object itself or ) the objects "name"
        for obj, attrS in self.O.items():
            if obj == obj_synonym:
                return obj
            if "name" in attrS and self.O.get_character_data("name", obj) == obj_synonym:
                return obj

        # the second argument is just used to identify the room and self
        # e.g. passing "room" maps to actual room
        room = self.O.get_holder(character)  

        # map local var value if it is same name as obj_name e.g. "myself" gets the key "character" which then maps to the character value and is returned
        mapped_obj = ""
        for obj, synonym_list in self.O["other_valid_obj_name"].items():
            for synonym in synonym_list:
                if obj_synonym == synonym:
                    mapped_obj = obj
                    break
            else:
                continue
            break
        for name, value in locals().items():
            if mapped_obj == name:
                return value

        # last check if mapped obj is valid
        if self.O.is_valid_obj(mapped_obj):
            return mapped_obj
        return "no obj found"

    def consume_cake(self, obj: objUID, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)

        # process synonym, in this case "cake" to map to any in your inventory
        if obj == "cake":
            for item in inventory:
                if item in ["strawberry_cake", "chocolate_cake", "vanilla_cake"]:
                    obj = item

        # map the rest of synonyms
        obj = self.map_to_actual_obj(obj, character)

        if obj in inventory:
            if do_print: 
                print("You lavishly ate the whole cake")
                self.delay()
                print("mouth was filled with icing")
                self.delay()
                print("Your eyes dilated...")
                self.delay()
                print("You can feel the sugar enter your")
                self.delay()
                print("blood stream")
                self.delay()
                print("You are now on sugar-rush")
            # always with extra turn
            current_turn_speed = self.O.get_character_data("turn_speed", character)
            self.O.set_character_data(character, "turn_speed", current_turn_speed + 100)
            return True
        if do_print: print("You do not have cake with you")
        return False

    def consume_coffee(self, obj: objUID, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in inventory:  # + room_holdings
            obj = "poisoned_coffee"
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("You sipped coffee in the middle of darkness")
                self.dotdotdot(False)
                print("while hearing your colleages fumble")
                self.delay()
                print("trying to find a flashlight")
                self.delay()
        if obj in inventory:
            if obj == "poisoned_coffee":
                self.consume_poison(obj, character, do_print)
            else:
                if do_print:
                    print(
                        "You felt a boost of energy!\n"
                        "It feels like you can do much more.\n"
                        'You are now "caffinated"!!'
                    )
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 120)
            return True
        return False

    def consume_poison(self, obj: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if obj in self.O.get_holding(character):
            if do_print:
                print(
                    "Ugh! You felt as if your stomach is about to explode\n"
                    "You hurried to the washroom..\n"
                    'You were "poisoned"!!'
                )
            self.O.remove_holding(obj, character)
            self.O.change_holder(character, room, "washroom")
            self.O.set_character_data(character, "turn_speed", 70)
            self.O.set_character_data(character, "skip_turn", 2)
            self.O.set_character_data(character, "skip_cause", f"you consumed {obj}")
            return True
        return False

    def consume_inedible(self, obj: str, character: str, do_print=True) -> bool:
        likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)
        inventory = self.O.get_holding(character)
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("Don't even try because you cannot see anything")
            return False
        if obj in self.O.get_holding(character) + self.O.get_holding(room):
            if obj == "laxative":
                if do_print:
                    print("I am not drinking that")
                return False
            else:
                if do_print:
                    print(f"You tried to eat {obj}")
                    self.delay()
                    print(f"your teeth clangs to the sound of you biting the {obj}")
                    self.delay()
                    print(f"Someone spotted you accross the room!")
                    self.delay()
                    print("Your likability decreases")
                self.O.set_character_data(character, "likability", likability - 2)
                return True
        return False

    def wait_time(self, character: None | objUID = None, do_print=True) -> bool:
        # the character var for something in the future e.g. maybe add a sereness item that boost player speed if they wait 5 times in a row
        if do_print:
            print("waiting", end="")
            self.dotdotdot()
        return True
    
    def hack_computer(self, destination: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        inventory = self.O.get_holding(character)
        LIKABILITY_CUT = 8

        if "usb_hacking_script" in inventory and room == "offices" and destination in ["workstation_1", "workstation_2", "workstation_3"]:
            if do_print:
                print("You insert the USB hacking script into the computer.")
                self.delay()
                print("The computer starts running the script...")
                self.delay(3)
            if destination == "workstation_1":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 1.")
                    print(f"{self.O.get_character_data("name", "player")} lost {LIKABILITY_CUT} likability for")
                player_likability = self.O.get_character_data("likability", "player")
                self.O.set_character_data("player", "likability", player_likability - LIKABILITY_CUT)
            elif destination == "workstation_2":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 2.")
                    print(f"{self.O.get_character_data("name", "NPC_1")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as his background.")
                philp_likability = self.O.get_character_data("likability", "NPC_1")
                self.O.set_character_data("NPC_1", "likability", philp_likability - LIKABILITY_CUT)
            elif destination == "workstation_3":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 3.")
                    print(f"{self.O.get_character_data("name", "NPC_2")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as her background.")
                serah_likability = self.O.get_character_data("likability", "NPC_2")
                self.O.set_character_data("NPC_2", "likability", serah_likability - LIKABILITY_CUT)
            return True
        else:
            if "usb_hacking_script" not in inventory:
                if do_print: print("You need the USB hacking script to perform this action.")
            if room != "offices":
                if do_print: print("You need to be in the offices to hack the computer.")
            return False
    
    def take_from_container(self, obj, container, character, do_print=True) -> bool:
        room = self.O.get_holder(character)
        # map to synonmys to use plus verify
        obj = self.map_to_actual_obj(obj, character)
        if obj == "no obj found":
            if do_print: print(f"{obj} is not in the game dictionary")
            return False
        container = self.map_to_actual_obj(container, character)
        if container == "no obj found":
            if do_print: print(f"{container} is not in the game dictionary")
            return False
        container_type = self.O.get_obj_type(container)
        if container_type == "room":
            if container != room:
                if obj in self.O.get_holding(container):
                    if do_print: print(f"You reached your invisible hands on {container}, another room")
                    if self.O.has_item_attribute("heavy", obj):
                        if do_print: 
                            print("But apparrently the object is too heavy to drag")
                            print("STILL, INVISIBLE HANDS?!")
                        return False
                    else:  # does not check max inventory using this way
                        if do_print:
                            print(f"taking the {obj} without anyone noticing and put it in your inventory")
                            print("ARE YOU GOD?!")
                        self.O.change_holder(obj, container, character)
                        return True
                else:
                    if do_print: print(f"Maybe try looking what the {container} is holding first")
                    return False
            else:
                if do_print: print("How are you supposed to shove an entire room in your pocket?")
        if self.O.get_holder(container) == room:
            if container_type == "static_character":
                if do_print: 
                    print("It's not allowed to steal belongings from the company employees")
                    print("but do try with your fellow interns!")
                return False
            if container_type == "character":
                npc_name = self.O.get_character_data("name", container)
                if obj in self.O.get_holding(container):
                    if do_print: print(f"You need to beat it out of {npc_name}")
                else:
                    if do_print: print(f"Try to examine {npc_name} to see if he/she is actually holding that")
                return False
            if container_type == "item" and self.O.has_item_attribute("container", container):
                if obj in self.O.get_holding(container):
                    inventory = self.O.get_holding(character)
                    if len(inventory) < self["variables"]["MAX_INVENTORY"]:
                        if do_print: print("Done")
                        self.O.change_holder(obj, container, character)
                        return True
                    else:
                        if do_print: print("You are carrying too many items")
                else: 
                    if do_print: 
                        print(f"Look at the {container}...")
                        print(f"Do you honestly see any {obj} there?")
            else:
                if do_print: print(f"{container} does not hold things")
        else:
            if do_print: print(f"You cannot see {self.O.get_character_data("name", container) if container_type in ["character", "static_character"] else container} in the room")
        return False

    
    def boss_inspection(self):
        contraband = ["laxative", "poisoned_coffee", "usb_hacking_script", "fake_resume", "suspicious_document"]

        """
        teleport everyone to office
        check each table of the people
        if person has their likability goes down?
        or get fired?

        """

        print("###########")
        print("#  EVENT  #")
        print("###########")
        print()
        msvcrt.getch()
        print("******** INSPECTION DAY ********")
        print()
        msvcrt.getch()
        print("The boss shouts from the office!")
        print()
        msvcrt.getch()
        print("BOSS: YOU MAGGOTS!")
        msvcrt.getch()
        print("TO THE WORKSTATIONS IMMEDIATELY!!!")
        msvcrt.getch()
        print()
        msvcrt.getch()
        print("everyone lines up in the offices room")
        msvcrt.getch()
        print("he looks at each of your tables")
        msvcrt.getch()
        print()
        print("you gulp as he inspects veery closely", end="")
        self.dotdotdot()
        msvcrt.getch()
        print()
        print("**********************************************")
        print()
        msvcrt.getch()

        for obj in self.O.keys():
            if self.O.get_obj_type(obj) == "character":
                # teleports players to offices for the event
                room = self.O.get_holder(obj)
                self.O.change_holder(obj, room, "offices")

                if obj in ["player", "NPC_1", "NPC_2"]:
                    current_likability = self.O.get_character_data("likability", obj)
                    for item in self.O.get_holding(obj):
                        if item in contraband:
                            if obj == "player":
                                print(f"Why do you have {item}???")
                                self.delay()
                                print(f"Are you trying to destroy the professinality")
                                self.delay()
                                print("of our establishment")
                            
                            self.O.set_character_data(obj, "likability", current_likability - 5)
                            break
                    else:
                        if obj == "player":
                            print("You are a good boi!")
                        self.O.set_character_data(obj, "likability", current_likability + 5)
        print()

    
    def place_obj(self, obj: objUID, container: objUID, character: objUID, do_print=True ) -> bool:
        inventory = self.O.get_holding(character)
        current_likability = self.O.get_character_data("likability", character)
        # map to synonmys to use plus verify
        obj = self.map_to_actual_obj(obj, character)
        if obj == "no obj found":
            if do_print: print(f"{obj} is not in the game dictionary")
            return False
        obj_type = self.O.get_obj_type(obj)
        if obj_type != "item":
            if do_print:
                print(f"you cannot put a {obj_type} on a container")
            return False
        if not self.O.has_item_attribute("container", container):
            if do_print:
                print(f"{container} is not a valid storage area.")
            return False
        else:
            if obj in inventory:
                if container == "workstation_1":
                    self.O.add_holding(obj, "workstation_1")
                    if do_print:
                        print(f"{obj} has been placed on {self.O.get_character_data("name", "player")}'s workstation.")
                        return True
                elif container == "workstation_2":
                    self.O.add_holding(obj, "workstation_2")
                    if do_print:
                        print(f"{obj} has been placed on Philp's workstation.") # fix hard for coding review 
                        return True
                elif container == "workstation_3":
                    self.O.add_holding(obj, "workstation_3")
                    if do_print:
                        print(f"{obj} has been placed on Serah's workstation.")
                        return True
                self.O.remove_holding(obj, character)
                return True
            else:
                if do_print: print("Maybe try finding the item first, that would be smart.")
            return False

    def make_poisoned_coffee(self, character: objUID, do_print=True) -> bool:
        # maybe make it work later for coffee in the room
        if all(x in self.O.get_holding(character) for x in ["coffee", "laxative"]):
            if do_print:
                print("Lacing coffee with poison muwahaha!")
                self.delay()
                print("Done")
            self.O.remove_holding("coffee", character)
            self.O.remove_holding("laxative", character)
            self.O.add_holding("poisoned_coffee", character)
            return True
        if do_print:
            print("I need to be holding both items")
        return False

    def give_coffee_or_poison(
        self, obj: objUID, to_character: objUID, from_character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(from_character)
        to_character = self.map_to_actual_obj(to_character, from_character)
        inventory = self.O.get_holding(from_character)

        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print:
                print(f"Giving to a {to_character}, are you mad?")
            return False
        gifted_name = self.O.get_character_data("name", to_character)
        current_friendliness = self.O.get_character_data("friendliness", to_character)
        if obj == "coffee" and "poisoned_coffee" in inventory:  # + room_holdings
            obj = "poisoned_coffee"
        if obj in inventory:
            if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
                if do_print:
                    print("You cannot see anyone in this darkdness")
                    self.delay()
                    print("but im sure they'd like a warm coffee to wait it out")
                return False
            if to_character in self.O.get_holding(room):
                spotted = rnd.randint(1, 100) <= 30
                if (
                    obj == "poisoned_coffee" and spotted
                ):  # 30% chance of getting spotted if giving poisoned coffee
                    if do_print:
                        print("You think I'd fall for it!")
                        self.delay()
                        print("I know you are handing me a poisoned coffee")
                        self.delay()
                        print(f"Friendliness with {gifted_name} decreased")
                    # positive
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(
                            to_character, "friendliness", current_friendliness - 1
                        )
                else:
                    if do_print:
                        print(f"{gifted_name}: Thanks for the coffee!")
                        self.delay()
                        print(f"Friendliness with {gifted_name} increased")
                    # negative
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(
                            to_character, "friendliness", current_friendliness + 1
                        )
                self.O.change_holder(obj, from_character, to_character)
                return True
            else:
                if do_print:
                    print(f"{gifted_name} isn't here go look for em")
        else:
            if do_print:
                print(f"I need to get more coffee before that")
        return False

    def give_cake(self, obj, taker:objUID, giver:objUID, do_print=True):
        cake_list = ["strawberry_cake","vanilla_cake","chocolate_cake"]
        # get the right cake by manual check
        if obj == "cake":
            for cake in cake_list:
                if cake in self.O.get_holding(giver):
                    obj = cake

        # verify objects
        obj = self.map_to_actual_obj(obj, giver)
        if obj == "no obj found":
            if do_print: print(f"{obj} is not in the game dictionary")
        # maps name to actual obj for characters
        taker = self.map_to_actual_obj(taker, giver)
        taker_type = self.O.get_obj_type(taker)
        if taker_type not in ["character", "static_character"]:
            if do_print: print(f"You cannot give to a {taker}")
            return False
        taker_name = self.O.get_character_data("name", taker)

        # giver will always be a valid character so no need to verify
        room = self.O.get_holder(giver)
        inventory = self.O.get_holding(giver)
        current_likability = self.O.get_character_data("likability", giver)

        if obj not in inventory:
            if do_print: print("I need to get cake first")
            return False

        # i.e. if giver is a "player"
        if self.O.get_character_data("uses_parser", giver):
            if taker == "boss":
                if "boss" not in self.O.get_holding(room):
                    print("Go look for the boss first")
                    return False

                # NPCs will give their cake then falls through to give your cake
                # but they can drop the cake or if you can steal them anytime
                else:
                    cake_list = [x for x in cake_list if x not in self.O.get_holding("player")]
                    # maybe just adjusting NPC likability once given
                    # npc = f"NPC_{i}"
                    # npc_likability = self.O.get_character_data("likability", npc)
                    # self.O.set_character_data(npc, "likability", npc_likability + 5)
                    for i,cake in enumerate(cake_list,1):
                        self.give_cake(cake, "boss", f"NPC_{i}", False)

        if taker == "boss":
            if obj == "chocolate_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability + 20
                )
                if do_print:
                    print(f"{taker_name}: I love chocolate cake! You're the best!")
            if obj == "strawberry_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability + 2
                )
                if do_print:
                    print(f"{taker_name}: I like chocolate more, but thank you!")
            if obj == "vanilla_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability - 10
                )
                if do_print:
                    print(f"{taker_name}: I HATE VANILLA CAKE! GET OUT OF MY SIGHT!")
            return True
        else:
            if taker in self.O.get_holding(room):
                if do_print: print("I'm sure the boss will like it better")
            else:
                if do_print: 
                    print(f"{taker_name} isn't in the room")
                    self.delay()
                    print(f"but should you really give to {taker_name}?")
            return False

    def load_events_data_structure(self, dict):
        for k, v in dict.items():
            self[k] = v

    def greet_at_game_start(self, character) -> None:
        print(
            """
                 _____      _                       ____   __  __            _____           _    
                |  __ \    | |                     / __ \ / _|/ _|          |  __ \         | |    
                | |__) |___| |_ _   _ _ __ _ __   | |  | | |_| |_ ___ _ __  | |__) |   _ ___| |__  
                |  _  // _ \ __| | | | '__| '_ \  | |  | |  _|  _/ _ \ '__| |  _  / | | / __| '_ \\
                | | \ \  __/ |_| |_| | |  | | | | | |__| | | | ||  __/ |    | | \ \ |_| \__ \ | | |
                |_|  \_\___|\__|\__,_|_|  |_| |_|  \____/|_| |_| \___|_|    |_|  \_\__,_|___/_| |_| """
        )

        self.delay(2)

        print(
            """ -----------------------------------------------------------------------------------------------------------------------------
                                                     STORY
             


As a new intern at Pentagon Inc., you must secure a return offer by currying favour with your boss. Compete against two other
interns in this cutthroat corporate environment, using clever tactics and collected items to gain the upper hand. Build
relationships, sabotage rivals, and manipulate situations to boost your standing. Use whatever means at your disposal to get
the full-time position as the job market is tough and you will never again have a job.




-------------------------------------------------------------------------------------------------------------------------------
                                                     OBJECTIVE


                       
Secure a return job offer by earning the boss's favour
Undermine rival interns using creative sabotage or forge friendships by working together
Explore the map and collect useful items to gain advantages
Discover hidden secrets and unlock unique endings
             
             
-------------------------------------------------------------------------------------------------------------------------------
"""
        )

        self.delay(3)
        print(self["event_dialogues"]["greet_at_game_start"])
        name = input("what is your name? \n> ")
        room = self.O.get_holder(character)
        self.O.set_character_data(character, "name", name)
        print(f"\nYou were dropped of at the {room}.\n")

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
                        self.delay()
                        self.dotdotdot()

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
                            self.dotdotdot()
                        else:
                            print(
                                "Invalid input. Email not forwarded. Should have put a proper input.\n"
                            )
                            self.dotdotdot()
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
                        self.delay()
                        print("I'M SO HAPPY TO HAVE YOU ALL HERE!")
                        self.delay()
                        print("I'M SO GRATEFUL FOR ALL OF YOU!")
                        self.delay()
                        print("DO YOU KNOW WHAT WILL MAKE THIS PARTY EVEN")
                        self.delay()
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

    def drink_medicine(self, obj, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj in inventory:
            if self.O.get_character_data("turn_speed", character) < 100:
                if do_print:
                    print("I drink medicine, now I feel good")
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 100)  # make healthy
                return True
            else:
                if do_print:
                    print("Why? You are perfectly healthy")
                return False
        if do_print:
            print("You don't have item!")
        return False

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
                            self.dotdotdot()
                            print("\nThe Text says: \nRule #1: Keep your desk clean. Apparently, the boss thinks clutter is a personal attack on his soul. Might be allergic to productivity too.\nRule #2: Always bring a flashlight to work. The lights go out sometimes and people just... disappear. Not saying it's haunted, but I'm not 'not' saying that either.\nRule #3 Make the boss happy. Even if it means pretending you care about his endless speeches. Nodding a lot helps.\nRule #4: Do some actual work. Apparently, staring intently at an empty spreadsheet does not count as “being productive.” Who knew?\nWeird tip: The secretary loves flowers... but I can not figure out which ones. Could just be stress gardening. Who knows.\nWeird tip: The secretary loves flowers... but I can not figure out which ones. Saw her fussing over some roses once. Could be nothing... or everything.\nHot Investment Tip: Buy Intern Coin. It is going to the moon! Trust me, I am basically a financial genius. Plus it is endorsed by our IT guy Steve Jobs.\nAlso by the way there is this suspicious safe in the boss's office... been wondering what is inside. Have not found out what was inside in my time here probably just old mementos.\n ")
                            self.dotdotdot()
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

    def boss_anniversary(self):
        self["variables"]["is_boss_anniversary"] = True

        # Teleport players
        for obj in self.O.keys():
            if self.O.is_valid_obj(obj) and (
                self.O.get_obj_type(obj) == "character" or obj == "boss"
            ):
                room = self.O.get_holder(obj)
                self.O.change_holder(obj, room, "meeting_room")

        print("###########")
        print("#  EVENT  #")
        print("###########")
        print()
        msvcrt.getch()
        print("******** BOSS ANNIVERSARY PARTY ********")
        print()
        msvcrt.getch()
        print("The old room speaker started ringing for Annoucement")
        msvcrt.getch()
        print("Everyone is to attend this mandatory event for our")
        msvcrt.getch()
        print("beloved Mr.Boss!! You are to leave your workstations")
        msvcrt.getch()
        print("Immediately!!!")
        print()
        msvcrt.getch()
        self.talk_to("boss", "player")
        msvcrt.getch()
        print("There are cakes in the cafeteria")
        msvcrt.getch()
        print("maybe the boss likes some")
        msvcrt.getch()
        print()
        print("**********************************************")
        print()
        msvcrt.getch()

        self.O.add_holding("strawberry_cake", "cafeteria")
        self.O.add_holding("vanilla_cake", "cafeteria")
        self.O.add_holding("chocolate_cake", "cafeteria")

    def is_secret_ending(self):
        for ending,is_true in self["variables"]["is_a_secret_endings"].items():
            if is_true:
                return ending
        return "no secret endings met"
    
    def thrown_obj_at_x(self, thrown_obj:objUID, thrown_to:objUID, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        current_likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)

        # map to synonmys to use plus verify
        thrown_obj = self.map_to_actual_obj(thrown_obj, character)
        if thrown_obj == "no obj found":
            if do_print: print(f"{thrown_obj} is not in the game dictionary")
            return False
        thrown_to = self.map_to_actual_obj(thrown_to, character)
        if thrown_to == "no obj found":
            if do_print: print(f"{thrown_to} is not in the game dictionary")
            return False
        obj_type = self.O.get_obj_type(thrown_obj)
        thrown_to_type = self.O.get_obj_type(thrown_to)
        
        # valid objects to throw and person to throw to
        if obj_type != "item":
            if do_print:
                print(f"How would you even throw that", end="")
                self.symsymsym("?")
            return False
        if thrown_to_type not in ["character", "static_character"]:
            if do_print: 
                print("What even would be the point of that", end="")
            return False
        victim_name = self.O.get_character_data("name", thrown_to)
        
        if thrown_obj not in inventory:
            if do_print: print("Maybe try finding the item first, that would be smart.")
            return False
        if thrown_to not in self.O.get_holding(room):
            if do_print: print(f"Maybe try finding {victim_name} first, that would be smart")
            return False
        if thrown_to_type == "character":
            if do_print:
                print(f"{victim_name} Ouch! why did you that!!")
                print(f"Friendliness with {victim_name} decreased")
            current_friendliness = self.O.get_character_data("friendliness", thrown_to)
            self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        if thrown_to_type == "static_character":
            if thrown_to == "boss":
                if do_print:
                    print(f"{victim_name} Bold strategy, I'm deducting 50 percent of your salary!")
                    self.delay()
                    print("your likabity to boss decreased")
                current_likability = self.O.get_character_data("likability", character)
                self.O.set_character_data(character, "likability", current_likability - 15)
            else:
                if do_print:
                    print("Wow did you really do that")
                    self.delay()
                    print("Just so you know, I know where you live")
                    self.delay()
                    print(f"Friendliness with {victim_name} decreased")
                current_friendliness = self.O.get_character_data("friendliness", thrown_to)
                self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        self.O.change_holder(thrown_obj, character, room)
        return True