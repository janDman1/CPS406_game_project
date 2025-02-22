from jan_subroutines import remove_comments, update_all_holders, show_screen, show_character_view, simple_command_parser_for_character
# import jaeden_subroutines
# import jake_subroutines
# import jonathan_parser

import json
import re
import random as rnd
from time import sleep
import os
from pprint import pprint

if False: ### Each item as its own # NO THANKS
    pass
    # # AREAS
    # Screen = {
    #     "id": 00,
    #     "type": "screen",
    #     "description": "Where the current things can be seen or viewed",
    #     "holder": None
    # }
    # washroom = {
    #     "id": 1,
    #     "type": "room",
    #     "holder": None,
    #     "description": "A clean and functional space designed for employee convenience, featuring modern fixtures and ample privacy. Nothing out of the ordinary except the supplies on the shelf behind the mirror..",
    #     "NSEW": [0,0,2,0]   # appends "To the EAST is the cafeteria"
    # }
    # cafeteria = {
    #     "id": 2,
    #     "type": "room",
    #     "holder": "screen",
    #     "description": "A small comfortable environment to enjoy meals or snack during break. Variety of food options can be bought here.",
    #     "NSEW": [0,0,3,1]  # append "To the WEST is the washroom, to the EAST is the main lobby"
    # }
    # main_lobby = {
    #     "id": 3,
    #     "type": "room",
    #     "description": "The central entrance area, designed to welcome visitors and employees. Fine decor hangs around the room, creating a professional and inviting atmosphere.",
    #     "NSEW": [0,0,0,2]   # appends "to the WEST is the cafeteria, to the NORTH is the secretary office, to the SOUTH is the building exit, to the EAST is the office area"
    # }

    # # ITEMS
    # coffee = {
    #     "holder": None,
    #     "description": "The rich aroma and warm, comforting glow of the cup offer a brief respite from the challenges of the virtual world. The item increases player's energy and focus.",
    #     "attributes": [
    #         "energize", 
    #         "friendliness"
    #     ]
    # }
    # laxative = {
    #     "holder": "player",
    #     "description": "A substance that promotes bowel movements, often used to relieve constipation. Do not misuse!",
    #     "attribute": [
    #         "poison"
    #     ]
    # }
    # poisoned_coffee = {  # coffee gets replaced with this when put laxative
    #     "holder": None,
    #     "description": "A dangerous drink that appears normal but has been secretly laced with a harmful substance. Consuming it can cause severe effects on the health.",
    #     "attribute": [
    #         "poison"
    #     ]
    # }

    # # CHARACTERS
    # player = {
    #     "likability": 0,
    #     "holder": "cafeteria"
    # }
    # NPC_1 = {
    #     "likability": 0,
    #     "friendliness": 2,  # neutral to the player
    #     "holder": "washroom"
    # }
    # NPC_2 = {
    #     "likability": 0,
    #     "friendliness": 0,  # aggressive to the player
    #     "holder": "washroom"
    # }

    # # SUBROUTINE e.g. put laxative on coffee
    # laxative_on_coffee = {
    #     "condition": [
    #         # obj[attr] = val
    #         ["laxative","holder",player],  # coffee["holder"] = null,
    #         ["coffee","holder",player]
    #     ],
    #     "action": [
    #         ["coffee","holder",None],
    #         ["laxative","holder",None],
    #         ["poisoned_coffee","holder",player]
    #     ],
    #     "description": "You are now holding the coffee laced with laxative"
    # }

# LOAD DATA FILE AS YOUR DATABASE TO USE
parsed_data_file = remove_comments(open("data.txt").read())
# print(parsed_data_file)
All_Data = json.loads(parsed_data_file)
O = All_Data["Objects"]  #Objects
V = {}
unprocessed_verbs = All_Data["Verbs"]
for k,v in unprocessed_verbs.items():
  try:
    V[int(k)] = set(v) #= v #
  except:
     V[k] = v # stay as "articles" and "prepositions" because not an action
# pprint(V)

#### TESTS ####
# pprint(Objects["coffee"])
# pprint(Objects["cafeteria"]["NSEW"][2])

# pprint(O["cafeteria"])

O["snacks"] = {
    "holder": "cafeteria",
    "description": "Something to temporary fill the hunger.",
    "attributes": [
		"energize"
    ]
}
O = update_all_holders(O)

# pprint(O["cafeteria"])
# pprint(O["snacks"])

# show_character_view("NPC_1",O)
# show_screen(O)
# pprint(O["player"])
# O["coffee"]["holder"] = "player"
# update_all_holders()
# pprint(O["player"])


#### GAME RUN ####

# def ending():
#     if ending_1:
#         return True
#     if ending_2:
#         return True
#     return False



# show_character_view("NPC_1",O)
# simple_command_for_character("NPC_1",O,V)
show_character_view("player",O)
simple_command_parser_for_character("player",O,V)

# USING percentage of having a chance of moving
world_speed = 100  #100 is default, 120 is energized, 70 is poisoned
skip_npc_turn = 0  #skips turn due to some event e.g. spilled coffee
skip_player_turn = 0
# while not ending():
#     if skip_npc_turn > 0:
#         skip_npc_turn -= 1
#         continue
#     else:
#         if rnd.randint(1,100) <= world_speed:
#             player_action()
#         if world_speed > 100 and  rnd.randint(1,100) <= world_speed-100:
#             player_action()  #see extra action
#     if skip_npc_turn > 0:
#         skip_npc_turn -= 1
#         continue
#     else:
#         npc_action()
#     boss_action()


# USING 2 for loops
player_speed,npc_speed = 1,1  #1:1 normal 
# player_speed,npc_speed = 6,5  #1.2:1 ratio  //energized
# player_speed,npc_speed = 7,10  #0.7:1 ratio  //poisoned
# for _ in range(player_speed):
# 	player_action()
# for _ in range(npc_speed):
# 	npc_action()
     
