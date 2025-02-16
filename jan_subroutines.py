import re

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


# update/add the "holding" attribute to traverse both ways
# without the third argument means unlimmited supply in room
def update_holding_for_items_holder(item, O, past_holder=None):
    # check the items with holders
    if "holder" in O[item]:
        curholder = O[item]["holder"]

        # if it has holder, add the attribute to the holder that it is holding this
        if curholder != None:
            # print(f"{curholder} is holding {k}")  # DEBUG
            if "holding" not in O[curholder]:
                    O[curholder]["holding"] = {item}
            else:
                O[curholder]["holding"].add(item)
        if past_holder is not None:
            O[past_holder]["holding"].remove(item)
    # return O
                
def update_all_holders(O):
    for k,v in O.items():
        update_holding_for_items_holder(k,O)
        # O = update_holding_for_items_holder(k,O)
    return O


def simple_command_parser_for_character(character, O, V):
    cmd = input("> ")
    while cmd not in ["Q", "Quit", "quit"]:  # OR not ending()
        cmd = cmd.split()
        cmd = [w for w in cmd if w not in V["articles"]]
        # print(f"input cmd is {cmd}")  # DEBUG
        for k,valid_cmdS in V.items():
            if any(w in cmd for w in valid_cmdS):
                # print(f"yes {cmd} is a valid command and key is {k}")  # DEBUG
                cur_room = O[character]["holder"]
                item = cmd[1] if len(cmd) > 1 else None
                # print(f"current room is {cur_room}")  # DEBUG
                if k in range(4):  # 0,1,2,3
                    if O[cur_room]["NSEW"][k] is None:
                        print(f"there is no exit to the {what_direction(k)}") #{V[k][1]}")
                    else:
                        O[character]["holder"] = O[cur_room]["NSEW"][k]
                        update_holding_for_items_holder(character,O)
                        # print(f"I am now at {O[character]["holder"]}")
                        show_character_view(character,O)
                if k == 4:
                    if item in O[cur_room]["holding"]:
                        O[item]["holder"] = character
                        update_holding_for_items_holder(item,O)
                if k == 5:
                    if item in O[character]["holding"]:
                        O[item]["holder"] = cur_room
                        update_holding_for_items_holder(item,O,character) # see the third argument
                if k == 6:
                    if item in O[cur_room]["holding"].union(O[character]["holding"]):
                        print(O[item]["description"])
                    if item in ["room", "Room"]:
                        # print(f"{cur_room}\n{O[cur_room]["description"]}")
                        show_character_view(character,O)
                if k == 7:
                    print(f"I am holding {O[character]["holding"]}")
                break  # valid command found therefore stop the search
        else: print("that is not a valid command\n\"H\" or \"help\" to view common commands")
        cmd = input("> ")


def what_direction(num):
    if num == 1: return "SOUTH"
    if num == 2: return "EAST"
    if num == 3: return "WEST"
    if num == 0: return "NORTH"

def show_room(room,O): #,direction=None):
    if O[room]["type"] == "room":
        print(O[room]["description"])
    items = []
    has_item = False
    for itm in O[room]["holding"]:
        if O[itm].get("type") != "room":
        # if O[i]["type"] == "item":
            has_item = True
            items.append(itm)
    if has_item:
        print(f"{items} is in the room.")
    
    for direction_num, destination in enumerate(O[room]["NSEW"]):
        if destination is not None:
            print(f"to the {what_direction(direction_num)} is {destination}")

def show_screen(O):
    room = next(iter(O["Screen"]["holding"]))
    show_room(room,O)
    

def show_character_view(character,O):
    print(f"{O[character]["holder"].upper()}")
    room = O[character].get("holder")
    show_room(room,O)
