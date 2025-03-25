from jan_game_base import remove_comments, ObjDict, Parser #Events
from jaeden_subroutines import Events_Expanded as Events
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

def do_action(subroutine_key:str, cmd: list, character:objUID, P:Parser, E:Events, verb_str:None|str=None, do_print=False) -> bool: # list [int|None,str|None,str|None,str|None]
    if cmd[0] is None: # no command so invalid action
        return False
    if verb_str is None:
        verb_str = P.get_random_verb_string(cmd[0])

    #### HOVER ANY OF THE E.FUNCTIONS TO SEE WHAT THEY DO ####
    if subroutine_key == "go_direction":
        return E.go_direction(cmd[0], character, do_print)
    if subroutine_key == "take_obj":
        return E.take_obj(cmd[1], character, do_print)
    if subroutine_key == "drop_obj":
        return E.drop_obj(cmd[1], character, do_print)
    if subroutine_key == "show_room":
        return E.show_character_view(character, do_print)  # `> look around` and `> examine room` both maps here, see lookup table in data.txt
    if subroutine_key == "show_inventory":
        return E.show_inventory(character, do_print)
    if subroutine_key == "read_obj_description":
        return E.read_obj_description(cmd[1], character, do_print)
    if subroutine_key == "karateyd":
        return E.karateyd(verb_str,cmd[1], character, do_print)
    if subroutine_key == "consume_coffee":
        return E.consume_coffee(cmd[1], character, do_print)
    if subroutine_key == "consume_poison":
        return E.consume_poison(cmd[1], character, do_print)
    if subroutine_key == "wait_time":
        return E.wait_time(character, False) #do_print)
    if subroutine_key == "make_poisoned_coffee":
        return E.make_poisoned_coffee(character, do_print)
    if subroutine_key == "consume_inedible":
        return E.consume_inedible(cmd[1], character, do_print)
    if subroutine_key == "give_coffee_or_poison":
        return E.give_coffee_or_poison(cmd[1], cmd[3], character, do_print)
    if subroutine_key == "give_obj":
        return E.give_obj(cmd[1], cmd[3], character, do_print)
    if subroutine_key == "email_work":
        return E.email_work(character, do_print)
    if subroutine_key == "talk_to":
        return E.talk_to(cmd[1], character, do_print)
    if subroutine_key == "drink_medicine":
        return E.drink_medicine(cmd[1], character, do_print)
    # if subroutine_key == "thrown_coffee_at_x":
    #   coffee_allover_character(cmd[3], character)  # checks character inventory if have coffee to throw and make obj2 (e.g. NPC_1) go to the washroom to waste turns
    # if subroutine_key == "thrown_obj_at_x":  # default behaviour e.g. `> thow laptop at Philip`
    #   obj_at_character(cmd[3], character)

    return False

# user/npc_input to action, how the character will interact with the world
def player_action(character:objUID, P:Parser, E:Events): #unparsed_cmd:str
    global unparsed_cmd
    
    valid_action = False
    while not valid_action:
        unparsed_cmd = input("> ")
        if unparsed_cmd in ["Q", "quit", "skip day"]: break  # or in dev_commands

        cmd = P.parse_input(unparsed_cmd)  # list[int|str|None]
        subroutine_key = P.find_subroutine_call(cmd)

        print(f"DEBUG cmd: {cmd}") # DEBUG
        print(f"DEBUG subroutine_key: {subroutine_key}")  # DEBUG

        verb_str = P.get_back_the_verb_string(int(cmd[0]), unparsed_cmd) if cmd[0] is not None else None
        valid_action = do_action(subroutine_key, cmd, character, P, E, verb_str, True)

def random_action(npc_character:objUID, P:Parser, E:Events):
    room = E.O.get_holder(npc_character)
    room_holdings = E.O.get_holding(room)
    inventory = E.O.get_holding(npc_character)

    valid_action = False
    while not valid_action:
        rand_action = rnd.choice(list(P["lookup_table"]))
        cmd = rand_action[:4]
        subroutine_key = rand_action[4]
        rand_obj1 = rnd.choice(list(P["game_dictionary"])) # + list(P["other_valid_obj_name"]))
        rand_obj2 = rnd.choice(list(P["game_dictionary"]))
        if cmd[1] == "*":
            cmd[1] = rand_obj1
        if cmd[3] == "*":
            cmd[3] == rand_obj2

        # print(f"cmd: {cmd}")
        # print(f"subroutine_key: {subroutine_key}")
        
        valid_action = do_action(subroutine_key, cmd, npc_character, P, E)

        # cmd = [None,None,None,None]
        # # cmd[0] = rnd.choice([0,1,2,3])  #dir
        # # objS = []
        # # for x in room_holdings + inventory:
        # #     # if E.O.get_obj_type(x) != "character":
        # #         objS.append(x)
        # # cmd[1] = rnd.choice(objS) if len(objS) != 0 else None  #obj
        # # cmd[0] = rnd.choice(list(P["verbs"]["10"]) + [cmd[0]])  #karate_verb plus cmd[0]

def character_action(character:objUID, P:Parser, E:Events, npc_type=0):
  if E.O.get_character_data("uses_parser",character): #character.uses_parser():
    player_action(character, P, E)
  else:
    if npc_type == 0:
        random_action(character, P, E)
    # elif npc_type == 1:
    # npc_ai_action(character)

def job_offer_with_coworker(pitcher):
    print("YOU ALL GOT JOB OFFER WITH YOUR COWORKERS")
    print("EVEN THOUGHT SOME OF YOU DID'T GET THE BOSS'S")
    print(f"FAVOUR, {pitcher.upper()} PITCHED IN FOR Y'ALL!")

def exclusive_job_offer(highest_likability):
    print("COMPETITIVENESS RAN IN THE ENTIRE")
    print("PERIOD OF THE INTERSHIP, BUT ONE")
    print("ONLY ONE STOOD ON TOP! THAT IS")
    print(f"{highest_likability.upper()} BEAT EVERYONE IN CAPABILITIES")

def no_one_gets_rehired():
    print("NO ONE OF YOU GOT THE BOSS'S FAVOUR")
    print("YOU ALL DID A BAD JOB IN THE INTERNSHIP")
    print("\"PROFESSIONALS YOU ARE NOT\" WAS THE")
    print("BOSS'S LASTS WORDS TO ALL OF YOU!!!")

likability_goal = 80
friendliness_goal = 5

def ending_result():
    global likability_goal, friendliness_goal, characterS
    friendliness_reached = True
    likability_reached = [True]*len(characterS)
    likability_reached_idxS = []
    pitcher = None
    for i,character in enumerate(characterS):
        current_friendliness = E.O.get_character_data("friendliness", character)
        if current_friendliness is not None and current_friendliness < friendliness_goal:
            friendliness_reached = False
        if E.O.get_character_data("likability", character) < likability_goal:
            likability_reached[i] = False
    for i,b in enumerate(likability_reached):
        if b:  # if b is True
            likability_reached_idxS.append(i)
    if len(likability_reached_idxS) > 0:
        pitcher = characterS[likability_reached_idxS[0]]
        highest_likability = characterS[likability_reached_idxS[0]]
        for i in likability_reached_idxS[1:]:
            if characterS[i] == "player":
                pitcher = "player"
            current_likability = E.O.get_character_data("likability", characterS[i])
            if current_likability > E.O.get_character_data("likability", highest_likability):
                highest_likability = characterS[i]
            
    
    if friendliness_reached and any(likability_reached):
        return job_offer_with_coworker(E.O.get_character_data("name", pitcher))  # ending 1
    if any(likability_reached):
        return exclusive_job_offer(E.O.get_character_data("name",highest_likability))  # ending 2
    if not any(likability_reached):
        return no_one_gets_rehired()  # ending 3


E.greet_at_game_start("player")

t = 0.1
game_day = 5
turns_in_a_day = 45
# character = "player"

characterS = []
for obj in O.keys():
  if E.O.get_obj_type(obj) == "character":
    characterS.append(obj)

unparsed_cmd = None  #input("> ")  # e.g. `> put A LaXaTiVe in the coffee`
# while game_day > 0 and unparsed_cmd not in ["Q", "quit"]: #while not ending():
for x in range(1,game_day+1):
    skip_day = False
    print("#########")
    print(f"# DAY {x} #")
    print("#####################################################################")
    for _ in range(turns_in_a_day):
        for character in characterS:
            print(f"{character.upper()} TURN")
            print("*************************************")
            skip_turn = E.O.get_character_data("skip_turn", character)
            turn_speed = E.O.get_character_data("turn_speed", character)
            print(f"DEBUG {character} skip_turn: {skip_turn}")  # DEBUG
            print(f"DEBUG {character} turn_speed: {turn_speed}")  # DEBUG
            if skip_turn > 0:
                print("skipping turn...")
                print(f"because {E.O.get_character_data("skip_cause", character)}")
                skip_turn -= 1
                E.O.set_character_data(character, "skip_turn", skip_turn)
            else:
                if rnd.randint(1,100) <= turn_speed:
                    character_action(character, P, E)
                # else:
                #     print("FALSE, you lost your turn!!!")  # DEBUG
                if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
                    print("(extra turn granted) caffinated in effect...")
                    character_action(character, P, E)  # see extra action
            print("*************************************\n")

            sleep(t)

            if unparsed_cmd in ["Q", "quit"]: break
            if unparsed_cmd == "skip day": 
                skip_day = True
                break
        else:  # aka is nobreak
            continue
        break
    else:  # aka is nobreak
        # go_home()  # prints go home OR even another function just being home doing things at home for some turns
        print("ITS TIME TO GO HOME")
        print("say bye to everyone")
        input("> ")
        continue
    if skip_day:
        skip_day = False
        print("You skipped the day! now what?\n")
        continue
    break
        
ending_result()  # show the result based on all stats
print()
print("YOU FINISHED THE GAME!")
print("CONGRATULATIONS!!!")
print("""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠈⠉⠒⠦⠄⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣾⣤⣤⣤⣤⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⡿⠉⣹⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠨⣆⠀⠀⠀⠀⠀
⠀⠀⠀⢠⡗⣡⣾⣿⠋⡘⠉⢳⡄⠀⠀⠀⠀⠀⠀⠀⠀⢿⣷⡀⠑⠄⠀⠀⠀
⠀⠀⢀⠎⠰⠁⢻⣿⣾⣄⣀⣼⣿⠀⠀⠀⠀⣠⣴⡖⠶⠒⢻⣷⣦⡈⢳⠀⠀
⠀⢠⡾⠀⡗⡀⠀⠉⠛⠿⢿⡿⠃⠀⠀⠀⢸⠀⢿⣇⣇⢀⣸⣿⠉⠁⢸⡀⠀
⠀⣣⠃⠀⢘⣈⣴⣶⡀⠒⠈⠀⠀⠀⠀⠀⠈⢆⠈⠛⠿⠿⠿⢻⠀⠀⠈⢷⠀
⢰⡇⠰⡉⠢⣀⡠⢂⠉⠒⠠⣀⠀⠀⠀⠀⠀⠀⠂⠄⠠⠄⠀⡎⠀⠀⠀⢸⠀
⢸⠀⠀⢱⠀⠀⠀⠈⠢⠠⠜⡇⠙⠢⡀⠀⠀⠀⠀⠈⠒⡒⢸⠀⠀⠀⠀⢸⡇
⢸⠀⠀⠀⢇⠀⠀⠀⠀⠀⠀⠙⠤⠴⢆⠁⢒⠒⠒⠄⠀⠈⠁⠀⠀⠀⠀⣿⠀
⣸⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠻⠠⠞⢸⠀⠀⠀⠀⠀⠀⢠⠸⠀
⢻⠀⠀⠀⠀⠰⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠎⠀⠀⠀⠀⠀⢀⢆⠇⠀
⠈⣇⠀⠀⠈⣆⠏⠁⣇⢠⠀⠀⠀⠀⠀⣀⡀⡰⠁⠀⠀⠀⠀⠀⠀⣼⠋⠀⠀
⠀⠘⣆⠀⠀⠈⠣⣔⠁⢸⠒⣑⠠⠐⠉⠉⠉⠀⠀⠀⠀⠀⠀⡠⠚⡘⠀⠀⠀
""")


# # def character_action(character):
# unparsed_cmd = None  #input("> ")  # e.g. `> put A LaXaTiVe in the coffee`
# while unparsed_cmd not in ["Q", "quit"]: #while not ending():

#     print(f"{character.upper()} TURN")
#     print("*************************************")
#     skip_turn = E.O.get_character_data("skip_turn", character)
#     print(f"DEBUG {character} skip_turn: {skip_turn}")  # DEBUG
#     if skip_turn > 0:
#         print("skipping turn...")
#         print(f"because {E.O.get_character_data("skip_cause", character)}")
#         skip_turn -= 1
#         E.O.set_character_data(character, "skip_turn", skip_turn)
#     else:
#         turn_speed = E.O.get_character_data("turn_speed", character)
#         print(f"DEBUG {character} turn_speed: {turn_speed}")  # DEBUG
#         if rnd.randint(1,100) <= turn_speed:
#             player_action(character, P, E)
#         else:
#             print("FALSE, you lost your turn!!!")  # DEBUG
#         if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
#             print("(extra turn granted) caffinated in effect...")
#             player_action(character, P, E)  # see extra action
#     print("*************************************\n")

#     sleep(t)

#     print("NPC_1 TURN")
#     print("*************************************")
#     skip_turn = E.O.get_character_data("skip_turn", "NPC_1")
#     print(f"DEBUG {"NPC_1"} skip_turn: {skip_turn}")  # DEBUG
#     if skip_turn > 0:
#         print("skipping turn...")
#         print(f"because {E.O.get_character_data("skip_cause", "NPC_1")}")
#         skip_turn -= 1
#         E.O.set_character_data("NPC_1", "skip_turn", skip_turn)
#     else:
#         turn_speed = E.O.get_character_data("turn_speed", "NPC_1")
#         print(f"NPC_1 turn_speed: {turn_speed}")  # DEBUG
#         if rnd.randint(1,100) <= turn_speed:
#             random_action("NPC_1", P, E)
#         else:
#             print("FALSE, you lost your turn!!!")  # DEBUG
#         if turn_speed > 100 and  rnd.randint(1,100) <= turn_speed-100:
#             random_action("NPC_1", P, E)
#     print("*************************************\n")

#     sleep(t)
    

# checked_likability = []
# def check_milestone():
#   if any likability == 50:
#     print(f"{character_x} has reached good boss connections")
#     checked_likability.append(character_x)



# USING percentage of having a chance to move per turn
world_speed = 70  #100 is default, 120 is energized, 70 is poisoned
skip_npc_turn = 0  #skips turn due to some event e.g. spilled coffee
skip_player_turn = 0
#     if skip_player_turn > 0:
#         skip_player_turn -= 1
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
     
