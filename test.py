from game_base import remove_comments, ObjDict
from subroutines import Events_Expanded as Events

import json
import os


parsed_data_file = remove_comments(open("data.txt").read())
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

# adds to Objects data while game is running
O["snacks"] = {
    "type": "item",
    "holder": "cafeteria",
    "description": "Something to temporary fill the hunger.",
    "attributes": ["energize"],
}
print("initiating holding of objects...")
# see the objects now has the "holding" initiated
O.initiate_holdings()
O.print_obj(
    "cafeteria"
)  # cafeteria is holding both "player" and the "snacks" we just created
# player is holding laxative
O.print_obj(obj)

print("****************************")

print("removing holder...")
O.remove_holder("laxative")

print("laxative's holder: ", end="")
print(O.get_holder("laxative"))

print(f"{obj} is holding: ", end="")
# still holding because remove_holder() only updates "holder"
print(O.get_holding(obj))

print("removing holding...")
O.remove_holding(
    "laxative", obj
)  # remove_holding() removes holding and also uses remove_holder() for holder update by default, put False third argument to disable
print(f"{obj} is holding: ", end="")
print(O.get_holding(obj))

print("adding holding...", end="")
O.add_holding(
    "coffee", obj
)  # same here, holder update by default, disable by putting False for third argument
print(f"{obj} is holding: ", end="")
print(O.get_holding(obj))

O.change_holder(
    "snacks", "cafeteria", obj
)  # removes holding from cafeteria and adds holding to player
O.print_obj(obj)

# for more implementation/usage of holding and holder
print("look at initiate_holdings()")

print("****************************")

print("to the north of cafeteria: ", O.find_next_room("N", "cafeteria"))
print("to the south of cafeteria: ", O.find_next_room("S", "cafeteria"))
print("to the east of cafeteria: ", O.find_next_room("E", "cafeteria"))
print("to the west of cafeteria: ", O.find_next_room("W", "cafeteria"))

print("****************************")

print(f"coffee has energize attribute: ", end="")
print(O.has_item_attribute("energize", "coffee"))

print(f"laxative has poison attribute: ", end="")
print(O.has_item_attribute("poison", "laxative"))

print("****************************")

char = "NPC_1"

print("###### Events CLASS #########")

E = Events()
E.load_object_dictionary(O)  # uses ObjDict
E.load_events_data_structure(All_Data["Events"])

E.show_character_view(obj)

print("****************************")

print("going south...")
# see it calls O.change_holder("player","cafeteria","washroom")
E.go_direction(2, obj)

E.O.print_obj(obj)
E.O.print_obj("cafeteria")
E.O.print_obj("washroom")

# for more data structure how-to usage
print("see other functions implementation in Events class")

print("****************************")
print("\n")

play_now = input("Ready to play the game?: ")
if play_now.upper() in ["YES", "Y", "YEAH"]:
    os.system("cls" if os.name == "nt" else "clear")
else:
    os.abort()
