from pprint import pprint
import re
import random as rnd
from time import sleep
import sys


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


type objUID = str


class ObjDict(dict):
    """
    Isolate game Data Structure and the Methods into this class.
    Also used for save and load feature.
    """

    # adds the dot (.) syntax notation for dictionary
    # e.g. Class.holder works as Class["holder"]
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def print_obj(self, obj: objUID) -> None:
        """For debugging :)"""
        if self.is_valid_obj(obj):
            obj_str = {obj: self[obj]}
            pprint(obj_str)

    def get_obj_type(self, obj: objUID) -> str:
        if self.is_valid_obj(obj):
            return self[obj]["type"]
        return "invalid object"

    def is_valid_obj(self, obj: objUID):
        if obj not in self:
            return False
        if not isinstance(self[obj], dict):
            return False
        for attr in ["type", "description", "holder"]:
            if attr not in self[obj].keys():
                return False
        return True

    def get_obj_description(self, obj: objUID) -> str:
        return self[obj]["description"]

    def initiate_holdings(self) -> None:
        """
        follow the object holder and add into holding,
        adding empty holding for the object
        (which might or might not be rewritten)
        while traversing all objects in ObjDict
        """
        visited = set()
        for obj in self.keys():
            if self.is_valid_obj(obj):
                src_obj = self[obj]["holder"]
                if src_obj is not None:
                    self.add_holding(obj, src_obj, False)
                    visited.add(src_obj)
                if obj not in visited:
                    self.add_holding(None, obj, False)

    def get_holder(self, obj: objUID) -> objUID:
        return self[obj]["holder"]

    def get_holding(self, obj: objUID) -> list[objUID]:
        return self[obj]["holding"].copy() if "holding" in self[obj] else []

    def add_holding(
        self, obj: None | objUID, src_obj: objUID, holder_update=True
    ) -> None:
        if self.is_valid_obj(src_obj):  # only works if source object exists/valid
            if obj is None:
                if "holding" not in self[src_obj]:
                    self[src_obj]["holding"] = []
            elif self.is_valid_obj(obj):
                if "holding" not in self[src_obj]:
                    self[src_obj]["holding"] = [obj]
                else:  # already has "holding"
                    self[src_obj]["holding"].append(obj)

                if holder_update:
                    self[obj]["holder"] = src_obj  # point obj to newest holder

    def remove_holding(self, obj: objUID, src_obj: objUID, holder_update=True) -> None:
        self[src_obj]["holding"].remove(obj)
        if holder_update:
            self.remove_holder(obj)

    def remove_holder(self, obj: objUID) -> None:
        self[obj]["holder"] = None

    def change_holder(self, obj: objUID, src_obj: objUID, dest_obj: objUID) -> None:
        self.remove_holding(obj, src_obj, False)
        self.add_holding(obj, dest_obj)

    type room_objUID = str

    def find_next_room(self, dir: str, room: room_objUID) -> room_objUID | None:
        if dir == "N":
            return self[room]["NSEW"][0]
        if dir == "S":
            return self[room]["NSEW"][1]
        if dir == "E":
            return self[room]["NSEW"][2]
        if dir == "W":
            return self[room]["NSEW"][3]
        return None

    def has_item_attribute(self, attr: str, obj: objUID) -> bool:
        return attr in self[obj]["attributes"]

    def get_character_data(self, data: str, char: objUID):  # -> str|int|None:
        if data not in [
            "name",
            "status",
            "likability",
            "dialogue",
            "friendliness",
            "turn_speed",
            "skip_turn",
            "skip_cause",
            "uses_parser",
        ]:
            raise KeyError(f"No {data} object Data in {char}")
        return self[char][data]

    def set_character_data(self, char: str, data: str, value: str | int | bool) -> None:
        if data not in [
            "name",
            "status",
            "likability",
            "dialogue",
            "friendliness",
            "turn_speed",
            "skip_turn",
            "skip_cause",
            "uses_parser",
        ]:
            raise KeyError(f"No {data} object Data in {char}")
        self[char][data] = value


class Events:
    """Class to modify the data structure"""

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
                    if "key_card" not in self.O.get_holding(character):
                        if do_print:
                            print("you don't have keycard to access room")
                        return False
                    else:
                        if do_print:
                            print("FINALLY", end="")
                            self.symsymsym("!")
                self.O.change_holder(character, room, next_room)
                self.show_character_view(character, do_print)
                return True
            if do_print:
                print("That way leads to nowhere")
        return False

    def show_character_view(self, character: objUID, do_print=True) -> bool:
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
                print(f"to the {self.direction(i)} is {next_room}")
        return True

    def print_list(self, lst: list[str], add_newline=True) -> None:
        for n, item in enumerate(lst):
            if item == "poisoned_coffee":
                item = "coffee"  # to perceive as normal coffee
            item = item.replace("_", " ")
            print(item, end="")
            if n < len(lst) - 1:
                if len(lst) == 2:
                    print(" and ", end="")
                else:
                    print(", ", end="")
                    if n == len(lst) - 2:
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
        if obj == "coffee" and "poisoned_coffee" in inventory:
            obj = "poisoned_coffee"
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
        obj = self.map_to_actual_obj(obj, character)
        if obj == "coffee" and "poisoned_coffee" in room_holdings_excluding_character:
            obj = "poisoned_coffee"

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
            if rnd.randint(1, 100) <= 50:
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
                        obj = rnd.choice(room_holdings_excluding_character)
                        room_holdings_excluding_character.remove(obj)
                        if len(room_holdings_excluding_character) <= 0:
                            break
                    else:
                        if do_print:
                            print("You actually found an item!")
                        # falls through if its actually in the room
                    if do_print:
                        print("You search every corner of the room")
                        self.delay()
                        print("but unfortunately cannot find anything")

        if obj in room_holdings_excluding_character:
            if len(inventory) < self["variables"]["MAX_INVENTORY"]:
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
        if (
            obj == "inventory" or obj == "room" or obj == room
        ):  # obj is the room the character is in
            self.show_character_view(character, do_print)
            return True
        obj = self.map_to_actual_obj(obj, character)
        obj_inventory = self.O.get_holding(obj)

        # For the safe
        if room == "boss_office" and obj == "safe":
            if do_print:
                print(f"{obj}: ", end="")
                print(self.O.get_obj_description(obj))
                self.delay()
                print("It requires a 4 digit code to open. Do you wish to try? (y/n)")

                while True:
                    user_input = input("> ").strip().lower()
                    if user_input == "y":
                        print("You decided to try opening the safe.")
                        # Add logic for attempting to open the safe here
                        correct_code = "1234"
                        attempts = 3

                        while attempts > 0:
                            code = input("Enter the 4 digit code: ")
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
                                        "You have run out of attempts. The safe is now locked."
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

        obj_type = self.O.get_obj_type(obj)

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

        if not do_print and obj_type != "invalid object":
            # skips below "room" "character" and "item" prints
            return True
        if obj_type == "room":
            print("Go there and find for yourself")
            return True

        # Get a description of the NPC Intern or Static Character
        if obj_type in ["character", "static_character"]:
            other_char_name = self.O.get_character_data("name", obj)
            if obj in room_holdings:
                print(self.O.get_obj_description(obj))
                if obj_type == "character":
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
                else:
                    if do_print:
                        print("uhh", end="")
                        self.dotdotdot()
                        print("no thank you")
                        self.delay()
                return True
            else:
                if do_print:
                    print("You can't see that")
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

    def map_to_actual_obj(self, obj_name: objUID, character: objUID) -> objUID:
        # map_to_actual_obj() ia a bit of a misnomer, the second argument is just used to identify the room and self

        for obj, attrS in self.O.items():
            if obj == obj_name:
                return obj
            if "name" in attrS and self.O.get_character_data("name", obj) == obj_name:
                return obj

        # map local var value if it is same name as obj_name e.g. "myself" gets the key "character" which then maps to the character value and is returned

        room = self.O.get_holder(character)  # this will be mapped if given "room"
        # inventory = self.O.get_holding(character)  # this will be mapped if given "inventory"  ## NOO, THIS WILL RETURN A LIST NOT AN objUID ##
        mapped_obj = "no obj found"
        for o, syn_lst in self.O["other_valid_obj_name"].items():
            for s in syn_lst:
                if obj_name == s:
                    mapped_obj = o
                    break
            else:
                continue
            break

        for name, value in locals().items():
            if mapped_obj == name:
                return value
        return mapped_obj

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
        if self.O.get_obj_type(to_character) != "character":
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

    def load_events_data_structure(self, dict):
        for k, v in dict.items():
            self[k] = v

    def greet_at_game_start(self, character) -> None:
        print(self["event_dialogues"]["greet_at_game_start"])
        name = input("what is your name? \n> ")
        room = self.O.get_holder(character)
        self.O.set_character_data(character, "name", name)
        print(f"\nYou were dropped of at the {room}.\n")


class Parser(dict):
    """Parser. what the class name says."""

    # adds the dot (.) syntax for dictionary
    # e.g. Class.holder works as Class["holder"]
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def fix_json_import(self) -> None:
        "fix data stuct lists into sets for better lookup"
        for k, l in self["verbs"].items():
            self["verbs"][k] = set(l)
        self["articles"] = set(self["articles"])
        self["prepositions"] = set(self["prepositions"])

    def load_game_dictionary(self, O: ObjDict) -> None:
        "makes a set of all the objects in game for object lookup"

        obj_nameS = set()
        for k in O.keys():
            if O.is_valid_obj(k):
                obj_nameS.add(k)
            if "name" in O[k]:
                nam = O[k]["name"]
                if nam != None:
                    obj_nameS.add(nam)

        valid_obj_synonyms = set()
        for _o, synonym_lst in O["other_valid_obj_name"].items():
            for s in synonym_lst:
                valid_obj_synonyms.add(s)

        self.game_dictionary = obj_nameS.union(valid_obj_synonyms)

    def parse_input(self, user_input: str) -> list[int | str | None]:
        """
        Parses user input into mapable [verb:int, obj1:str, prep:str, obj2:str] for lookup in lookup_table e.g. [put, laxative, in, coffee].
        Verifies if verbs, objects, and preposition are valid.
        """
        verb, obj1, prep, obj2 = None, None, None, None
        unprocessed_list = user_input.split()
        v_idx = None
        o1_idx = None
        o2_idx = None
        processed1_list = []
        processed2_list = []

        for a in self["articles"]:
            for _ in range(len(unprocessed_list)):
                try:
                    unprocessed_list.remove(a)
                except:
                    continue

        for v, synonymS in self["verbs"].items():
            for s in synonymS:
                try:
                    v_idx = unprocessed_list.index(s)
                    try:
                        processed1_list = unprocessed_list[v_idx + 1 :]
                    except:
                        pass
                    verb = int(v)
                    break
                except ValueError:
                    continue
            if verb is not None:
                break

        # obj1 eaten
        for valid_obj in self["game_dictionary"]:
            try:
                o1_idx = processed1_list.index(valid_obj)
                break
            except:
                continue

        # obj2 eaten
        for valid_obj in self["game_dictionary"]:
            try:
                next_obj_idx = processed1_list.index(valid_obj)
                if next_obj_idx != o1_idx:
                    o2_idx = next_obj_idx
                    break
                continue
            except:
                continue

        if o2_idx is not None and o1_idx is not None:
            if o1_idx > o2_idx:
                o1_idx, o2_idx = o2_idx, o1_idx
        obj1 = processed1_list[o1_idx] if o1_idx is not None else None
        obj2 = processed1_list[o2_idx] if o2_idx is not None else None

        # obj1 will never be None before obj2
        processed2_list = (
            []
            if o2_idx is None and o1_idx is None
            else (
                processed1_list[o1_idx:]
                if o2_idx is None
                else processed1_list[o1_idx : o2_idx + 1]
            )
        )

        # preposition eaten
        for w in processed2_list:
            if w in self["prepositions"]:
                prep = w
        if prep not in processed2_list:
            prep = None

        return [verb, obj1, prep, obj2]

    type subroutineID = str

    def find_subroutine_call(self, cmd: list[int | str | None]) -> subroutineID:
        """maps user input to subroutine_key (aka eventID), optimally using trie"""
        impossible_val = 10  # impossible because max score is 3
        score = [impossible_val] * len(self["lookup_table"])
        for i, match in enumerate(self["lookup_table"]):
            if cmd == match[:4]:
                return match[4]
            match_verb = cmd[0] == match[0]
            match_obj1 = cmd[1] == match[1] or match[1] == "*" and cmd[1] is not None
            match_preb = cmd[2] == match[2] or match[2] == "*" and cmd[2] is not None
            match_obj2 = cmd[3] == match[3] or match[3] == "*" and cmd[3] is not None
            if match_verb and match_obj1 and match_obj1 and match_preb and match_obj2:
                score[i] = 0
                if match[1] == "*":
                    score[i] += 1
                if match[2] == "*":
                    score[i] += 1
                if match[3] == "*":
                    score[i] += 1
        best_match = 0 if score[0] is not impossible_val else None
        min_so_far = score[0]
        for i, v in enumerate(score[0:]):
            if v is not impossible_val:
                if v < min_so_far:
                    min_so_far = v
                    best_match = i
        return (
            self["lookup_table"][best_match][4]
            if best_match is not None
            else "no match"
        )

    def get_back_the_verb_string(self, verb: int, unprocessed_cmd: str) -> str:
        for v in self["verbs"][str(verb)]:
            if v in unprocessed_cmd:
                return v
        return "no verb found"

    def get_random_verb_string(self, verb: int) -> str:
        return rnd.choice(list(self["verbs"][str(verb)]))

    def help_command(self) -> dict:
        # print("Commands: ")
        # pprint(self["verbs"])

        
        print("COMMANDS [ARGUMENTS]")
        for cmd in self["lookup_table"]:
            verb,obj1,prep,obj2,_ = cmd
            verb = list(self["verbs"][str(cmd[0])])[0]
            obj1 = "[room/item/character]" if obj1 == "*" else "" if obj1 == None else cmd[1]
            prep = str(self["prepositions"]).split("/") if prep == "*" else "" if prep == None else cmd[2]
            obj2 = "[room/item/character]" if obj2 == "*" else "" if obj2 == None else cmd[3]
            print(f"{verb} {obj1} {prep} {obj2}")
            
        """
        loop through lookup_table, get the first row, get the first element of the row, verb[number], get second element,  f"verb[number]: second element"
        verbs[list(P["lookup_table"])]
        
        
        """
        return True
