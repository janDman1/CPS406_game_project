from utils import delay, dotdotdot, symsymsym
import random as rnd

type objUID = str

class BasicActions:


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
                            symsymsym("!")
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
                delay()
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
                delay()
                print("Unless", end="")
                dotdotdot()
                print("(the thoughts disappeared from your mind)")
            return False

        # "flashlight" in inventory is a placeholder, change to if holding any item with "illuminate" attribute later
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("You probed the surface until", end="")
                dotdotdot()
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
                                delay()
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
                delay()
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
                    dotdotdot()
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
    

    def wait_time(self, character: None | objUID = None, do_print=True) -> bool:
        # the character var for something in the future e.g. maybe add a sereness item that boost player speed if they wait 5 times in a row
        if do_print:
            print("waiting", end="")
            dotdotdot()
        return True