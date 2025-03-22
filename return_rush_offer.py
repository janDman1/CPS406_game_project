from jan_game_base import remove_comments, ObjDict, Events, Parser
# import jaeden_subroutines
# import jake_dialogues
# import jonathan_testers

import json
import random as rnd
import os
# import re
from time import sleep
# from pprint import pprint

#**************************************** 13

#**************************************** 98


#### TESTS ####
# example using my functions here

parsed_data_file = remove_comments(open("data.txt").read())
# print(parsed_data_file)
All_Data = json.loads(parsed_data_file)
O = ObjDict(All_Data["Objects"])

obj = "player"

print("###### ObjDict CLASS #########")

# the dot (.) syntax notation in action
# instead of O["NPC_1"] I can access using O.NPC_1 
print(O.NPC_1["description"])
# but don't use the ObjDict like this, use its methods, see below 

print("****************************")

print(f"{obj} type: ", end="")
print(O.get_obj_type(obj))

print(f"{obj} description: ", end="")
print(O.get_obj_description(obj))

print(f"{obj} holder: ", end="") 
print(O.get_holder(obj))

print("****************************")

O["snacks"] = {  # adds to Objects data while game is running
    "type": "item",
    "holder": "cafeteria",
    "description": "Something to temporary fill the hunger.",
    "attributes": [
		"energize"
    ]
}
print("initiating holding of objects...")
O.initiate_holdings()  # see the objects now has the "holding" initiated
O.print_obj("cafeteria")  # cafeteria is holding both "player" and the "snacks" we just created
O.print_obj(obj)  # player is holding laxative

print("****************************")

print("removing holder...")
O.remove_holder("laxative")

print("laxative's holder: ", end="")
print(O.get_holder("laxative"))

print(f"{obj} is holding: ", end="")
print(O.get_holding(obj))  # still holding because remove_holder() only updates "holder" 

print("removing holding...")
O.remove_holding("laxative", obj)  # remove_holding() removes holding and also uses remove_holder() for holder update by default, put False third argument to disable
print(f"{obj} is holding: ", end="")
print(O.get_holding(obj)) 

print("adding holding...", end="")
O.add_holding("coffee", obj)  # same here, holder update by default, disable by putting False for third argument
print(f"{obj} is holding: ", end="")
print(O.get_holding(obj))

O.change_holder("snacks","cafeteria",obj)  # removes holding from cafeteria and adds holding to player
O.print_obj(obj)

# for more implementation/usage of holding and holder
print("look at initiate_holdings()")

print("****************************")

print( "to the north of cafeteria: ", O.find_next_room("N","cafeteria"))
print( "to the south of cafeteria: ", O.find_next_room("S","cafeteria"))
print( "to the east of cafeteria: ", O.find_next_room("E","cafeteria"))
print( "to the west of cafeteria: ", O.find_next_room("W","cafeteria"))

print("****************************")

print(f"coffee has energize attribute: ", end="")
print(O.has_item_attribute("energize", "coffee"))

print(f"laxative has poison attribute: ", end="")
print(O.has_item_attribute("poison", "laxative"))

print("****************************")

char = "NPC_1"
# print(O.get_character_data("description", char))  # will return error, no data found. why? because only works for ["name", "status", "likability", "friendliness", "skip_turn", "turn_speed"]

print("###### Events CLASS #########")

E = Events()
E.load_object_dictionary(O)  # uses ObjDict

E.show_character_view(obj)

print("****************************")

print("going south...")
E.go_direction(2, obj)  # see it calls O.change_holder("player","cafeteria","washroom")

E.O.print_obj(obj)
E.O.print_obj("cafeteria")
E.O.print_obj("washroom")

# for more data structure how-to usage
print("see other functions implementation in Events class")

print("****************************")
print("\n")

play_now = input("Ready to play the game?: ")
if play_now.upper() in ["YES", "Y", "YEAH"]:
  os.system('cls' if os.name == 'nt' else 'clear')
else:
  os.abort()

#********************* 210

#### GAME RUN ####

## INITIALIZE ##

# LOAD DATA FILE AS YOUR DATABASE TO USE
parsed_data_file = remove_comments(open("data.txt").read())
# print(parsed_data_file)
All_Data = json.loads(parsed_data_file)
O = ObjDict(All_Data["Objects"])
O["snacks"] = {  # adds to Objects data while game is running
    "type": "item",
    "holder": "cafeteria",
    "description": "Something to temporary fill the hunger.",
    "attributes": [
		"energize"
    ]
}
O.initiate_holdings()
E = Events()
E.load_object_dictionary(O)
E.load_events_data_structure(All_Data["Events"])
P = Parser(All_Data["Commands"])
P.fix_json_import()
P.load_game_dictionary(O)

# def ending():
#     if ending_1:
#         return True
#     if ending_2:
#         return True
#     return False


## ACTUAL GAME ##

type objUID = str  # just means objUID is type string

# user/npc_input to action, how the character will interact with the world
def player_action(character:objUID, unparsed_cmd:str, parser:Parser) -> bool:
    cmd = P.parse_input(unparsed_cmd)  # list[int|str|None]
    subroutine_key = P.find_subroutine_call(cmd)
    print(f"DEBUG cmd: {cmd}") # DEBUG
    print(f"DEBUG subroutine_key: {subroutine_key}")  # DEBUG

   #### HOVER ANY OF THE E.FUNCTIONS TO SEE WHAT THEY DO ####
    valid_action = False
    # while not valid_action:
    if subroutine_key == "go_direction":
        valid_action = \
        E.go_direction(cmd[0], character)
    if subroutine_key == "take_obj":
        valid_action = \
        E.take_obj(cmd[1], character)
    if subroutine_key == "drop_obj":
        valid_action = \
        E.drop_obj(cmd[1], character)
    if subroutine_key == "show_room":
        valid_action = \
        E.show_character_view(character)  # `> look around` and `> examine room` both maps here, see lookup table in data.txt
    if subroutine_key == "show_inventory":
        valid_action = \
        E.show_inventory(character)
    if subroutine_key == "read_obj_description":
        valid_action = \
        E.read_obj_description(cmd[1], character)
    if subroutine_key == "karateyd":
        verb_str = P.get_back_the_verb_string(cmd[0], unparsed_cmd)
        valid_action = \
        E.karateyd(verb_str,cmd[1], character)
    if subroutine_key == "consume_coffee":
        valid_action = \
        E.consume_coffee(cmd[1], character)
    if subroutine_key == "consume_poison":
        valid_action = \
        E.consume_poison(cmd[1], character)
    # if subroutine_key == "thrown_coffee_at_x":
    #   coffee_allover_character(cmd[3], character)  # checks character inventory if have coffee to throw and make obj2 (e.g. NPC_1) go to the washroom to waste turns
    # if subroutine_key == "thrown_obj_at_x":  # default behaviour e.g. `> thow laptop at Philip`
    #   obj_at_character(cmd[3], character)
    if not valid_action:
        print("not a valid action")
    
    return valid_action


# def do_action(subroutine_key, cmd, character):
#     #### HOVER ANY OF THE E.FUNCTIONS TO SEE WHAT THEY DO ####
#     valid_action = False
#     # while not valid_action:
#     if subroutine_key == "go_direction":
#         valid_action = \
#         E.go_direction(cmd[0], character)
#     if subroutine_key == "take_obj":
#         valid_action = \
#         E.take_obj(cmd[1], character)
#     if subroutine_key == "drop_obj":
#         valid_action = \
#         E.drop_obj(cmd[1], character)
#     if subroutine_key == "show_room":
#         valid_action = \
#         E.show_character_view(character)  # `> look around` and `> examine room` both maps here, see lookup table in data.txt
#     if subroutine_key == "show_inventory":
#         valid_action = \
#         E.show_inventory(character)
#     if subroutine_key == "read_obj_description":
#         valid_action = \
#         E.read_obj_description(cmd[1], character)
#     if subroutine_key == "karateyd":
#         verb_str = P.get_back_the_verb_string(cmd[0], unparsed_cmd)
#         valid_action = \
#         E.karateyd(verb_str,cmd[1], character)
#     if subroutine_key == "consume_coffee":
#         valid_action = \
#         E.consume_coffee(cmd[1], character)
#     if subroutine_key == "consume_poison":
#         valid_action = \
#         E.consume_poison(cmd[1], character)
#     # if subroutine_key == "thrown_coffee_at_x":
#     #   coffee_allover_character(cmd[3], character)  # checks character inventory if have coffee to throw and make obj2 (e.g. NPC_1) go to the washroom to waste turns
#     # if subroutine_key == "thrown_obj_at_x":  # default behaviour e.g. `> thow laptop at Philip`
#     #   obj_at_character(cmd[3], character)
#     if not valid_action:
#         print("not a valid action")
    
#     return valid_action

def random_action(npc_character):
    room = E.O.get_holder(npc_character)
    room_holdings = E.O.get_holding(room)
    inventory = E.O.get_holding(npc_character)

    valid_action = False
    while not valid_action:
        subroutine_key = rnd.choice(["go_direction","take_obj","drop_obj","show_room","show_inventory","read_obj_description","karateyd","consume_coffee","consume_poison"]) #"consume_coffee","consume_poison"])#
        # # print(f"I do {subroutine_key}...")

        # cmd = [None,None,None,None]
        # # cmd[0] = rnd.choice([0,1,2,3])  #dir
        # # objS = []
        # # for x in room_holdings + inventory:
        # #     # if E.O.get_obj_type(x) != "character":
        # #         objS.append(x)
        # # cmd[1] = rnd.choice(objS) if len(objS) != 0 else None  #obj
        # # cmd[0] = rnd.choice(list(P["verbs"]["10"]) + [cmd[0]])  #karate_verb plus cmd[0]

        # # this don't work, too much combinations that doesn't match
        # # cmd[0] = rnd.choice(list(P["verbs"]))
        # # cmd[1] = rnd.choice(list(P["game_dictionary"]) + list(P["other_valid_obj_name"]))
        # # subroutine_key = P.find_subroutine_call(cmd)

        # rand_action = rnd.choice(list(P["lookup_table"]))
        # cmd = rand_action[:4]
        # rand_obj = rnd.choice(list(P["game_dictionary"])) # + list(P["other_valid_obj_name"]))
        # if cmd[1] == "*":
        #     cmd[1] = rand_obj
        # subroutine_key = rand_action[4]

        # print(f"cmd: {cmd}")
        # print(f"subroutine_key: {subroutine_key}")
        
        # valid_action = do_action(subroutine_key, cmd, npc_character)

        if subroutine_key == "go_direction":
            dir = rnd.choice([0,1,2,3])
            valid_action = \
            E.go_direction(dir, npc_character)
        if subroutine_key == "take_obj":
            objS = []
            for x in room_holdings:
                if E.O.get_obj_type(x) != "character":
                    objS.append(x)
            obj = rnd.choice(objS) if len(objS) != 0 else None
            valid_action = \
            E.take_obj(obj, npc_character)
        if subroutine_key == "drop_obj":
            obj = rnd.choice(inventory) if len(inventory) != 0 else None
            valid_action = \
            E.drop_obj(obj, npc_character)
        if subroutine_key == "show_room":
            valid_action = \
            E.show_character_view(npc_character)  # `> look around` and `> examine room` both maps here, see lookup table in data.txt
        if subroutine_key == "show_inventory":
            valid_action = \
            E.show_inventory(npc_character)
        if subroutine_key == "read_obj_description":
            objs_room_n_inv = room_holdings + inventory
            obj = rnd.choice(objs_room_n_inv) if len(objs_room_n_inv) != 0 else None
            valid_action = \
            E.read_obj_description(obj, npc_character)
        if subroutine_key == "karateyd":
            karate_verb = rnd.choice(list(P["verbs"]["10"]))
            # verb_str = rnd.choice(["punch","kick","karate","beat"])
            obj = rnd.choice(room_holdings)
            valid_action = \
            E.karateyd(karate_verb, obj, npc_character)
        if subroutine_key == "consume_coffee":
            valid_action = \
            E.consume_coffee("coffee", npc_character)
        if subroutine_key == "consume_poison":
            obj = rnd.choice(["laxative","poisoned_coffee"])
            valid_action = \
            E.consume_poison("laxative", npc_character)
        
        if not valid_action:
            print("not a valid action")
        # return valid_action



character = "player"
E.greet_at_game_start(character)
E.show_character_view(character)
# def character_action(character):
unparsed_cmd = None  #input("> ")  # e.g. `> put A LaXaTiVe in the coffee`
while unparsed_cmd not in ["Q", "quit"]: #while not ending():

    print(f"{character.upper()} TURN")
    print("*************************************")
    while(True): 
        skip_turn = E.O.get_character_data("skip_turn", character)
        print(f"DEBUG {character} skip_turn: {skip_turn}")  # DEBUG
        if skip_turn > 0:
            print("skipping turn...")
            print(f"because {E.O.get_character_data("skip_cause", character)}")
            skip_turn -= 1
            E.O.set_character_data(character, "skip_turn", skip_turn)
            break
        turn_speed = E.O.get_character_data("turn_speed", character)
        print(f"DEBUG {character} turn_speed: {turn_speed}")  # DEBUG
        valid_action = False
        if rnd.randint(1,100) <= turn_speed:
            unparsed_cmd = input("> ")
            if unparsed_cmd in ["Q", "quit"]: break
            valid_action = \
                player_action(character, unparsed_cmd, P)  # aka character_action("player")
        if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
            print("(extra turn granted) caffinated in effect...")
            unparsed_cmd = input("> ")
            if unparsed_cmd in ["Q", "quit"]: break
            valid_action = \
                player_action(character, unparsed_cmd, P)  #see extra action
        if valid_action:
            break
    print("*************************************\n")

    t = 2

    sleep(t)

    print("NPC_1 TURN")
    print("*************************************")
    # while(True):
    skip_turn = E.O.get_character_data("skip_turn", "NPC_1")
    print(f"DEBUG {"NPC_1"} skip_turn: {skip_turn}")  # DEBUG
    if skip_turn > 0:
        print("skipping turn...")
        print(f"because {E.O.get_character_data("skip_cause", "NPC_1")}")
        skip_turn -= 1
        E.O.set_character_data("NPC_1", "skip_turn", skip_turn)
    else:
        turn_speed = E.O.get_character_data("turn_speed", "NPC_1")
        print(f"NPC_1 turn_speed: {turn_speed}")  # DEBUG
        if rnd.randint(1,100) <= turn_speed:
            random_action("NPC_1")
        else:
            print("FALSE, you lost your turn!!!")  # DEBUG
        if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
            random_action("NPC_1")
    print("*************************************\n")

    sleep(t)

    # print("NPC_2 TURN")
    # print("*************************************")
    # # while(True):
    # skip_turn = E.O.get_character_data("skip_turn", "NPC_2")
    # print(f"DEBUG {"NPC_2"} skip_turn: {skip_turn}")  # DEBUG
    # if skip_turn > 0:
    #     print("skipping turn...")
    #     print(f"because {E.O.get_character_data("skip_cause", "NPC_2")}")
    #     skip_turn -= 1
    #     E.O.set_character_data("NPC_2", "skip_turn", skip_turn)
    #     # break
    # else:
    #     turn_speed = E.O.get_character_data("turn_speed", "NPC_2")
    #     print(f"NPC_2 turn_speed: {turn_speed}")  # DEBUG
    #     if rnd.randint(1,100) <= turn_speed:
    #         random_action("NPC_2")
    #         # if random_action("NPC_2"): break
    #     else:
    #         print("FALSE, you lost your turn!!!")  # DEBUG
    #         # break
    #     if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
    #         random_action("NPC_2")
    #         # if random_action("NPC_2"): break
    # print("*************************************\n")

    # sleep(t)
    



# checked_likability = []
# def check_milestone():
#   if any likability == 50:
#     print(f"{character_x} has reached good boss connections")
#     checked_likability.append(character_x)

# def character_action(char):
#   if O[char].uses_parser():
#     player_action(char)
#   else:
#     npc_ai_action(char)

# characterS = []
# for x in O.keys():
#   if O[x].get_obj_type() == "character":
#     characterS.append(x)
# for char in characterS:
#   character_action(char)

# USING percentage of having a chance to move per turn
world_speed = 70  #100 is default, 120 is energized, 70 is poisoned
skip_npc_turn = 0  #skips turn due to some event e.g. spilled coffee
skip_player_turn = 0
# while not ending():
#     if skip_npc_turn > 0:
#         skip_npc_turn -= 1
#         continue
#     else:
#         if rnd.randint(1,100) <= world_speed:
#             player_action()  # aka character_action("player")
#         if world_speed > 100 and  rnd.randint(1,100) <= world_speed-100:
#             player_action()  #see extra action
#     if skip_npc_turn > 0:
#         skip_npc_turn -= 1
#         continue
#     else:
#         npc_action()  # aka character_action("NPC_X")
#     boss_action()


# USING 2 for loops to have X number of moves per turn
# player_speed,npc_speed = 1,1  #1:1 normal 
# player_speed,npc_speed = 6,5  #1.2:1 ratio  //energized
player_speed,npc_speed = 7,10  #0.7:1 ratio  //poisoned
# for _ in range(player_speed):
# 	player_action()
# for _ in range(npc_speed):
# 	npc_action()
     
