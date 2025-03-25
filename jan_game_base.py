from pprint import pprint 
import re
import random as rnd
from time import sleep
import sys

# print

# # this is giving me errors currently: 'dict' object has no attribute 'print'
# # Overwrite the built-in print function to include flush=True by default
# def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=True):
#     __builtins__.print(*objects, sep=sep, end=end, file=file, flush=flush)

def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, string)

type objUID = str  # just means objUID is type string

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
        self[attr]=value

    def print_obj(self, obj:objUID) -> None:
        """For debugging :)"""
        if self.is_valid_obj(obj):
            obj_str = {obj: self[obj]}
            pprint(obj_str)
    
    def get_obj_type(self, obj:objUID) -> str:
        if self.is_valid_obj(obj):
            return self[obj]["type"]
        return "invalid object"

    def is_valid_obj(self, obj:objUID):
        if obj not in self:
            return False
        if not isinstance(self[obj], dict):
            return False
        for attr in ["type", "description", "holder"]:
            if attr not in self[obj].keys():
                return False
        return True
    
    def get_obj_description(self, obj:objUID) -> str:
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

    def get_holder(self, obj:objUID) -> objUID:
        return self[obj]["holder"]
    
    def get_holding(self, obj:objUID) -> list[objUID]:
        return self[obj]["holding"].copy() if "holding" in self[obj] else []
    
    def add_holding(self, obj:None|objUID, src_obj:objUID, holder_update=True) -> None:
        if self.is_valid_obj(src_obj): # only works if source object exists/valid
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

        # if self.is_valid_obj(src_obj) and self.is_valid_obj(obj) or obj is None:
        #     if "holding" not in self[src_obj]:
        #         self[src_obj]["holding"] = [obj] \
        #             if obj is not None else []
        #     else:
        #         if obj is not None:
        #             self[src_obj]["holding"].append(obj)
        #     if holder_update:
        #         self[obj]["holder"] = src_obj  # point obj to newest holder

    def remove_holding(self, obj:objUID, src_obj:objUID, holder_update=True) -> None:
        self[src_obj]["holding"].remove(obj)
        if holder_update:
            self.remove_holder(obj)

    def remove_holder(self, obj:objUID) -> None:
        self[obj]["holder"] = None

    def change_holder(self, obj:objUID, src_obj:objUID,  dest_obj:objUID) -> None:
        self.remove_holding(obj, src_obj, False)
        self.add_holding(obj, dest_obj)

    type room_objUID = str

    def find_next_room(self, dir:str, room:room_objUID) -> room_objUID|None:
        if dir == "N":
            return self[room]["NSEW"][0]
        if dir == "S":
            return self[room]["NSEW"][1]
        if dir == "E":
            return self[room]["NSEW"][2]
        if dir == "W":
            return self[room]["NSEW"][3]
        return None
        
    def has_item_attribute(self, attr:str, obj:objUID) -> bool:
        return attr in self[obj]["attributes"]
    
    def get_character_data(self, data:str, char:objUID): #-> str|int|None:
        if data not in ["name", "status", "likability", "friendliness", "turn_speed", "skip_turn", "skip_cause", "uses_parser"]:
            raise KeyError(f"No {data} object Data in {char}")
        return self[char][data]
    
    def set_character_data(self, char:str, data:str, value:str|int|bool) -> None:
        if data not in ["name", "status", "likability", "friendliness", "turn_speed", "skip_turn", "skip_cause","uses_parser"]:
            raise KeyError(f"No {data} object Data in {char}")
        self[char][data] = value
    


class Events:  # (ObjDict):
    """Class to modify the data structure"""

    # add the [] syntax notation like dictionary
    # e.g. Class["variables"] works as Class.variables
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def load_object_dictionary(self, obj_dict:ObjDict) -> None:
        self.O = obj_dict

    def go_direction(self, dir:int, character:objUID, do_print=True) -> bool:
        """move to direction e.g. North, using character"""
        # override if you want to expand dialogues e.g. to say something else other than default "you cannot go there", you could say "that's the ladies room, you are not allowed there" if going north of washroom
        if self.O.is_valid_obj(character) and self.O.get_obj_type(character) == "character":
            room = self.O.get_holder(character)
            dir_converted = self.direction(dir)[0]
            next_room = self.O.find_next_room(dir_converted, room)
            if next_room is not None:
                if next_room == "secret_room":
                    if "key_card" not in self.O.get_holding(character):
                        if do_print: print("you don't have keycard to access room")  
                        return False
                    else:
                        if do_print: 
                            print("FINALY", end="")
                            self.symsymsym("!")
                self.O.change_holder(character, room, next_room)
                self.show_character_view(character, do_print)
                return True
            if do_print: print("you cannot go there")
        return False
            
    def show_character_view(self, character:objUID, do_print=True) -> bool:
        """deduce the room the character is in and print what is there and valid directions of next rooms"""
        # override if you want to customize
        if not do_print:  # no need to show anything
            return True
        room = self.O.get_holder(character)
        # change to send_to_console if implementing formatter class
        print(room.upper())
        print(self.O.get_obj_description(room))
        room_holdings = self.O.get_holding(room)
        room_holdings.remove(character)
        if len(room_holdings) > 0:
            for n,item in enumerate(room_holdings):
                if self.O.get_obj_type(item) in ["character", "static_character"]:
                    room_holdings[n] = self.O.get_character_data("name", item)
            print(f"You can see ", end="")
            self.print_list(room_holdings)
        for i in ["N","S","E","W"]:
            next_room = self.O.find_next_room(i, room)
            if next_room is not None:
                print(f"to the {self.direction(i)} is {next_room}")
        return True

    def print_list(self, lst: list[str], add_newline=True) -> None:
        for n,item in enumerate(lst):
            if item == "poisoned_coffee":
                item = "coffee"  # to perceive as normal coffee
            item = item.replace("_", " ")
            print(item, end="")
            if n<len(lst)-1:
                if len(lst) == 2:
                    print(" and ", end="")
                else:
                    print(", ", end="")
                    if n == len(lst)-2:
                        print("and ", end="")
            else:
                if add_newline:
                    print()
    
    def direction(self, dir: int|str):
        if dir in [1, "S"]: return "SOUTH"
        if dir in [2, "E"]: return "EAST"
        if dir in [3, "W"]: return "WEST"
        if dir in [0, "N"]: return "NORTH"
        # print(f"MISS: you entered {dir}")  # DEBUG

    def drop_obj(self, obj:objUID, character:objUID, do_print=True) -> bool:
        """check character holder (aka the room) and drop item there"""
        inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in inventory:
            obj = "poisoned_coffee"
        if self.O.is_valid_obj(obj) and obj in inventory:
            room = self.O.get_holder(character)
            self.O.change_holder(obj, character, room)
            if do_print: print("Done")
            return True
        return False
    
    def take_obj(self, obj:objUID, character:objUID, do_print=True) -> bool:
        """put obj1 to character holdings (aka inventory). also update holder"""
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        if obj == "coffee" and "poisoned_coffee" in room_holdings:
            obj = "poisoned_coffee"
        if obj in room_holdings and obj != character:
            if len(self.O.get_holding(character)) < self["variables"]["MAX_INVENTORY"]:
                self.O.change_holder(obj, room, character)
                if do_print: print("Done")
                return True
            else: 
                if do_print: print("You have too much stuff already")
        return False
    
    def show_inventory(self, character:objUID, do_print=True) -> bool:
        # override if you want to customize
        if not do_print:  # no need to show anything
            return True
        inventory = self.O.get_holding(character)
        if len(inventory) > 0:
            print(f"You have with you ", end="")
            self.print_list(inventory)
        else:
            print("You aren't carrying anything.")
        return True #False
    
    def read_obj_description(self, obj:objUID, character:objUID, do_print=True) -> bool:
        # override if you want to customize
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        # objs_in_view = room_holdings + char_inventory
        # items_in_view.append(self.O.get_holding(room)).append(self.O.get_holding(character))
        # if obj in game_dictionary 
        if obj == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            obj = "poisoned_coffee"
        if obj == "room" or obj == room:  # obj is the room the character is in
            self.show_character_view(character, do_print)
            return True
        obj = self.map_to_actual_obj(obj, character)
        obj_inventory = self.O.get_holding(obj)
        # map_obj_name = self.map_to_actual_obj(obj, character)
        # if map_obj_name != "no obj found":
        #     obj = map_obj_name
        obj_type = self.O.get_obj_type(obj)
        if not do_print and obj_type != "invalid object":  # no need to show anything  
            # skips below "room" "character" and "item" prints
            return True
        if obj_type == "room":
            print("Go there and find for yourself")
            return True
        if obj_type in ["character","static_character"]:
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
        elif obj_type == "item":
            if obj in room_holdings or obj in char_inventory: #objs_in_view:
                print(f"{obj}: ", end="")
                print(self.O.get_obj_description(obj))
                return True
            else:
                print("That isn't there!")
                return False
        return False
    
    def karateyd(self, verb:str, obj:objUID, character:objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            obj = "poisoned_coffee"
        if obj == "room" or obj == room:  # either the valid obj name "room" or specified the actual room the character is in e.g. "cafeteria" can both be used
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
        # obj_type = None
        # if self.O.is_valid_obj(obj):
        #     obj_type = self.O.get_obj_type(obj)
        # else:
        #     if obj == "room":
        #         obj_type = "room"
        #     if obj in ["self","yourself"]:
        #         obj_type = "character"
        obj_type = self.O.get_obj_type(obj)
        if obj_type == "room":
            return False  # can't kick or throw tantrum in another room
        if obj_type == "item":
            if obj in room_holdings or obj in char_inventory:
                if obj in ["coffee","poisoned_coffee"]:
                    if do_print:
                        print("you broke the mug, ", end="")
                        self.delay()
                        print("hurt yourself, ", end="")
                        self.delay()
                        print("and spilled coffee", end="")
                        self.dotdotdot()
                        print("*good job*")
                        self.delay()
                    where_coffee_at = room if "coffee" in room_holdings \
                        else character if "coffee" in char_inventory \
                        else None
                    if where_coffee_at is not None:
                        self.O.remove_holding("coffee", where_coffee_at)
                else:
                    if do_print:
                        print("uhh", end="")
                        self.dotdotdot()
                        print("no thank you")
                        self.delay()
                return True
            else:
                if do_print: print("You can't see that")
                return False
        if obj_type == "character":
            victim_name = self.O.get_character_data("name", obj)
            inventory = self.O.get_holding(obj)
            dropped_item = rnd.choice(inventory) if len(inventory) != 0 else None
            current_friendliness = self.O.get_character_data("friendliness", obj)

            if obj in self.O.get_holding(room):
                if do_print:
                    if obj == character:  #in ["self", "yourself"]:  #
                        print("Ughh, I hate myself!")
                        print("What is wrong with me!")
                        print(f"You {verb} yourself")
                        print(f"You stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}")
                    else:
                        print(f"You {verb} {victim_name}", end="") #, flush=True)
                        self.dotdotdot()
                        # print(f"{obj}: Fuck you!") //okay maybe this isn't appropriate
                        print(f"{victim_name} stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}")
                        self.delay()
                        print(f"\"shit man!\"")
                        self.delay()
                        print(f"{victim_name} gets up, and brushes you off")
                        self.delay()
                        print(f"Friendliness with {victim_name} decreased")

                if dropped_item is not None:
                    self.O.change_holder(dropped_item, obj, room)
                    if self.O.get_character_data("uses_parser", character):
                        self.O.set_character_data(obj, "friendliness", current_friendliness-1)

                return True
            else:
                if do_print: print(f"{victim_name} isn't even there dummy")
                return False
        return False
    
    def delay(self, speed_number=2) -> None:
        sys.stdout.flush()
        if speed_number == 0:
            pass
        if speed_number == 1:
            sleep(.3)
        if speed_number == 2:
            sleep(1.2)
        if speed_number == 3:
            sleep(2.3)
        if speed_number == 4:
            sleep(4)
        if speed_number == 5:
            sleep(7)

    def symsymsym(self, symbol:str, newline=True) -> None: 
        self.delay()
        for _ in range(3):
            print(f"{symbol}", end="") #, flush=True) #
            self.delay(1)
        if newline:
            print()

    def dotdotdot(self, newline=True) -> None:
        self.symsymsym(".", newline)
    
    def map_to_actual_obj(self, obj_name:objUID, character:objUID) -> objUID: #, character=None):
        for obj,attrS in self.O.items():
            if obj == obj_name:
                return obj
            if "name" in attrS and self.O.get_character_data("name", obj) == obj_name:
                return obj
        
        # map local var value if it is same name as obj_name e.g. "myself" gets the key "character" which then maps to the character value and is returned

        room = self.O.get_holder(character)  # this will be mapped if given "room"
        inventory = self.O.get_holding(character)  # this will be mapped if given "inventory"
        mapped_obj = "no obj found"
        # valid_obj_synonyms = set()
        for o,syn_lst in self.O["other_valid_obj_name"].items():
            for s in syn_lst:
                if obj_name == s:
                    mapped_obj = o
                    break
            else:  # aka if nobreak
                continue
            break
                # valid_obj_synonyms.add(s)
        
        for name, value in locals().items():
            # print(f"name: {name}, ", end="")  # DEBUG
            # print(f"value: {value}")  # DEBUG
            if mapped_obj == name:
                # print(f"mapped_obj: {mapped_obj}, name: {name}, value: {value}")  # DEBUG
                return value
        # print(f"mapped_obj: {mapped_obj}")  # DEBUG
        return mapped_obj
        
        # room = self.O.get_holder(character) if character is not None else None
        # if obj_name in self.O:
        #     return obj_name
        # if obj_name in ["room", "around"]:
        #     # if room is None:
        #     #     raise TypeError(f"add a second argument character to map_to_actual_obj() to find the room")
        #     # else:
        #         return room
        # if obj_name in ["self", "yourself", "myself"]:
        #     return character
        # if obj_name == "Philip":
        #     return "NPC_1"
        # if obj_name == "Serah":
        #     return "NPC_2"

        # return "no obj found"
    

    def consume_coffee(self, obj:objUID, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in inventory: #+ room_holdings
            obj = "poisoned_coffee"
        if obj in inventory:
            if obj == "poisoned_coffee":
                self.consume_poison(obj, character, do_print)
            else:
                if do_print: print("You felt a boost of energy!\n"
                "It feels like you can do much more.\n"
                "You are now \"caffinated\"!!")
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 120)
            return True
        return False
    
    def consume_poison(self, obj:objUID, character:objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if obj in self.O.get_holding(character):
            if do_print: print("Ugh! You felt as if your stomach is about to explode\n"
            "You hurried to the washroom..\n"
            "You are \"poisoned\"!!")
            self.O.remove_holding(obj, character)
            self.O.change_holder(character,room,"washroom") 
            self.O.set_character_data(character, "turn_speed", 70)
            self.O.set_character_data(character, "skip_turn", 2)
            self.O.set_character_data(character, "skip_cause", f"you consumed {obj}")
            return True
        return False
    
    def consume_inedible(self, obj:str, character:str, do_print=True) -> bool:
        likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)
        if obj == "laxative":
            print("I am not drinking that")
            return False
        if obj in self.O.get_holding(character) + self.O.get_holding(room):
            if do_print: 
                print(f"You tried to eat {obj}")
                self.delay()
                print(f"your teeth clangs to the sound of you biting the {obj}")
                self.delay()
                print(f"Someone spotted you accross the room!")
                self.delay()
                print("Your likability decreases")
            self.O.set_character_data(character, "likability", likability-2)
            return True
        return False
    
    def wait_time(self, character:None|objUID = None, do_print=True) -> bool: #
        # literally do nothing, not even increment turn_skip
        # if character is not None:
        #     pass
        # the character var for something in the future e.g. maybe add a sereness item that boost player speed if they wait 5 times in a row
        if do_print:
            print("waiting", end="")
            self.dotdotdot()
        return True

    def make_poisoned_coffee(self, character:objUID, do_print=True) -> bool:
        # room = self.O.get_holder(character)
        # maybe make it work later for coffee in the room
        if all(x in self.O.get_holding(character) for x in ["coffee","laxative"]): # + self.O.get_holding(room):
            if do_print:
                print("Lacing coffee with poison muwahaha!")
                self.delay()
                print("Done")
            self.O.remove_holding("coffee", character)
            self.O.remove_holding("laxative", character)
            self.O.add_holding("poisoned_coffee", character)
            return True
        if do_print: print("I need to be holding both items") #I need both the items in my inventory")
        return False
    
    def give_coffee_or_poison(self, obj:objUID, to_character:objUID, from_character:objUID, do_print=True) -> bool:
        room = self.O.get_holder(from_character)
        to_character = self.map_to_actual_obj(to_character, from_character)  # map_to_actual_obj() ia a bit of a misnomer, the second argument is just used to identify the room and self 
        inventory = self.O.get_holding(from_character)
        if self.O.get_obj_type(to_character) != "character":
            if do_print: print(f"Giving to a {to_character}, are you mad?")
            return False
        gifted_name = self.O.get_character_data("name", to_character)
        current_friendliness = self.O.get_character_data("friendliness", to_character)
        if obj == "coffee" and "poisoned_coffee" in inventory: #+ room_holdings
            obj = "poisoned_coffee"
        if obj in inventory:
            if to_character in self.O.get_holding(room):
                spotted = rnd.randint(1,100) <= 30
                if obj == "poisoned_coffee" and spotted:  # 30% chance of getting spotted if giving poisoned coffee
                    if do_print:
                        print("You think I'd fall for it!")
                        self.delay()
                        print("I know you are handing me a poisoned coffee")
                        self.delay()
                        print(f"Friendliness with {gifted_name} decreased")
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(to_character, "friendliness", current_friendliness-1)
                else:
                    if do_print:
                        print(f"{gifted_name}: Thanks for the coffee!")
                        self.delay()
                        print(f"Friendliness with {gifted_name} increased")
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(to_character, "friendliness", current_friendliness+1)
            else:
                if do_print: print(f"{gifted_name} isn't here go look for em")
        else:
            if do_print: print(f"I need to get more coffee before that")
        return True
    
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
                if gifted_name == "Steve Jobs" and obj == "usb_hacking_script": # and give item hacking script
                    self.O.remove_holding(obj, from_character)
                    self.O.set_character_data(to_character, "friendliness", current_friendliness+5)
                    return True
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

    
    def load_events_data_structure(self, dict):
        for k,v in dict.items():
            self[k] = v
        # self["variables"] = dict["variables"]
        

    def greet_at_game_start(self, character) -> None:
        print(self["event_dialogues"]["greet_at_game_start"])
        name = input("what is your name? \n> ")
        room = self.O.get_holder(character)
        self.O.set_character_data(character, "name", name)
        print(f"\nYou were dropped of at the {room}.\n")

    def get_dialogue(self, dialo):
        pass


class Parser(dict):
    """Parser. what the class name says."""

    # adds the dot (.) syntax for dictionary 
    # e.g. Class.holder works as Class["holder"] 
    def __getattr__(self, attr):
        return self[attr]
    
    def __setattr__(self, attr, value):
        self[attr]=value

    # NO NEED TO CONVERT CMD_IDs TO INT,
    # JUST USE to_string() or to_int()
    # def load_parser_datastruct(self, CommandsDict): #__init__()
    #     # self.preposition = CommandsDict[]
    #     for k,v in self["verbs"].items():
    #         try:
    #             self[int(k)] = set(v) #= v #
    #             self.pop(k)
    #         except:
    #             self[k] = v # stay as "articles" and "prepositions" because no synonyms

    def fix_json_import(self) -> None:
        "fix data stuct lists into sets for better lookup"
        for k,l in self["verbs"].items():
            self["verbs"][k] = set(l)
        self["articles"] = set(self["articles"])
        self["prepositions"] = set(self["prepositions"])
        # self["other_valid_obj_name"] = self["other_valid_obj_name"] #set(self["other_valid_obj_name"])

    def load_game_dictionary(self, O:ObjDict) -> None:
        "makes a set of all the objects in game for object lookup"

        obj_nameS = set()
        for k in O.keys():
            if O.is_valid_obj(k):
                obj_nameS.add(k)
            if "name" in O[k]:
                obj_nameS.add(O[k]["name"])
        
        valid_obj_synonyms = set()
        for _o,synonym_lst in O["other_valid_obj_name"].items():
            for s in synonym_lst:
                valid_obj_synonyms.add(s)
        
        self.game_dictionary = obj_nameS.union(valid_obj_synonyms)

    def parse_input(self, user_input:str) -> list[int|str|None]:
        """
        Parses user input into mapable [verb:int, obj1:str, prep:str, obj2:str] for lookup in lookup_table e.g. [put, laxative, in, coffee].
        Verifies if verbs, objects, and preposition are valid.
        """
        verb, obj1, prep, obj2 = None, None, None, None
        unprocessed_list = user_input.split()
        v_idx = None
        o1_idx = None
        o2_idx = None
        processed1_list = []  # index 0 will be obj1
        processed2_list = []  # index -1 (last idx) will be obj2
        # print(f"unprocessed: {unprocessed_list}") # DEBUG

        # remove articles
        for a in self["articles"]:
            for _ in range(len(unprocessed_list)):  # O(n^2) i know its bad
                try:
                    unprocessed_list.remove(a)
                except:
                    continue
        
        # verb eaten
        for v,synonymS in self["verbs"].items():
            for s in synonymS:
                try:
                    v_idx = unprocessed_list.index(s)
                    try:
                        processed1_list = unprocessed_list[v_idx+1:]
                    except:
                        pass
                    verb = int(v)
                    break
                except ValueError:
                    continue
            if verb is not None:
                break
        # print(f"processed1: {processed1_list}") # DEBUG
        
        # STILL NEED TO KNOW OBJ1, OBJ2 else Events methods wont work
        # i.e. if there was no match and went with default "*"
        # What would the "*" match in the objects? it can't.
        # for match in self["lookup_table"]:
        #     for word in match:


        # obj1 eaten
        for valid_obj in self["game_dictionary"]: #.union(valid_obj_synonyms): #self["other_valid_obj_name"]): #
            try:
                o1_idx = processed1_list.index(valid_obj)
                break
            except:
                continue

        #obj2 eaten
        for valid_obj in self["game_dictionary"]: #.union(valid_obj_synonyms): #self["other_valid_obj_name"]): #
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
        processed2_list = [] if o2_idx is None and o1_idx is None else processed1_list[o1_idx:] if o2_idx is None else processed1_list[o1_idx:o2_idx+1]
        # print(f"processed2: {processed2_list}") # DEBUG

        # preposition eaten
        for w in processed2_list:
            if w in self["prepositions"]:
                prep = w
        if prep not in processed2_list:
            prep = None

        return [verb, obj1, prep, obj2]
    

    type subroutineID = str

    def find_subroutine_call(self, cmd: list[int|str|None]) -> subroutineID:
        """maps user input to subroutine_key (aka eventID), optimally using trie"""
        impossible_val = 10 # impossible because max score is 3
        score = [impossible_val] * len(self["lookup_table"])
        for i,match in enumerate(self["lookup_table"]):
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
        for i,v in enumerate(score[0:]):
            if v is not impossible_val:
                if v < min_so_far:
                    min_so_far = v
                    best_match = i
        # print(f"score: {score}") # DEBUG
        # print(f"best_match: {best_match}") # DEBUG
        # print(self["lookup_table"][best_match] if best_match is not None else "") # DEBUG
        return self["lookup_table"][best_match][4] if best_match is not None else "no match"
    
    def get_back_the_verb_string(self, verb:int, unprocessed_cmd:str) -> str:
        for v in self["verbs"][str(verb)]:
            if v in unprocessed_cmd:
                return v
        return "no verb found"
    
    def get_random_verb_string(self, verb:int) -> str:
        return rnd.choice(list(self["verbs"][str(verb)]))

