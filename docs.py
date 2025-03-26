"""
def add_holding(self, obj:None|objUID, src_obj:objUID, holder_update=True) -> None:

if self.is_valid_obj(src_obj) and self.is_valid_obj(obj) or obj is None:
    if "holding" not in self[src_obj]:
        self[src_obj]["holding"] = [obj] \
            if obj is not None else []
    else:
        if obj is not None:
            self[src_obj]["holding"].append(obj)
    if holder_update:
        self[obj]["holder"] = src_obj  # point obj to newest holder

        
def karateyd(self, verb: str, obj: objUID, character: objUID, do_print=True) -> bool:

# # maybe add if there is obj in the room we can hit it, but this is after we can do more karate on other item instead of just saying "no thank you"
                # if len(room_holdings) > 0:
                #     if do_print: print(f"and you actually hit something!")
                #     # if do_print: print(f"You put the object down readying to {verb} it")
                #     obj = rnd.choice(room_holdings)

def map_to_actual_obj(
        self, obj_name: objUID, character: objUID
    ) -> objUID:

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

    class Parser:
    
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

    # STILL NEED TO KNOW OBJ1, OBJ2 else Events methods wont work
        # i.e. if there was no match and went with default "*"
        # What would the "*" match in the objects? it can't.
        # for match in self["lookup_table"]:
        #     for word in match:


    class Events_Expanded(Events): <- in subroutines.py

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

"""
