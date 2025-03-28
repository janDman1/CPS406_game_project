import re

from events import Events
from obj_dict import ObjDict
from parser import Parser

import json
import random as rnd
import os
import msvcrt


"""
RETURN OFFER RUSH GAME

"""

#### GAME RUN ####


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


## INITIALIZE ##


# LOAD DATA FILE AS YOUR DATABASE TO USE
parsed_data_file = remove_comments(open("data.txt").read())
All_Data = json.loads(parsed_data_file)

O = ObjDict(All_Data["Objects"])
# adds to Objects data while game is running
O["snacks"] = {
    "type": "item",
    "holder": "cafeteria",
    "description": "Something to temporary fill the hunger.",
    "attributes": ["energize"],
}
O.initiate_holdings()
E = Events()
E.load_object_dictionary(O)
E.load_events_data_structure(All_Data["Events"])
P = Parser(All_Data["Commands"])
P.fix_json_import()
P.load_game_dictionary(O)


## ACTUAL GAME ##

type objUID = str


def do_action(
    subroutine_key: str,
    cmd: list,
    character: objUID,
    P: Parser,
    E: Events,
    verb_str: None | str = None,
    do_print=False,
) -> bool:
    if cmd[0] is None:
        return False
    if verb_str is None:
        verb_str = P.get_random_verb_string(cmd[0])

    #### HOVER ANY OF THE E.FUNCTIONS TO SEE WHAT THEY DO ####
    match subroutine_key:
        case "go_direction":
            return E.go_direction(cmd[0], character, do_print)
        case "take_obj":
            return E.take_obj(cmd[1], character, do_print)
        case "drop_obj":
            return E.drop_obj(cmd[1], character, do_print)
        case "show_room":
            # `> look around` and `> examine room` both map here
            return E.show_character_view(character, do_print)
        case "show_inventory":
            return E.show_inventory(character, do_print)
        case "read_obj_description":
            return E.read_obj_description(cmd[1], character, do_print)
        case "karateyd":
            return E.karateyd(verb_str, cmd[1], character, do_print)
        case "consume_coffee":
            return E.consume_coffee(cmd[1], character, do_print)
        case "consume_poison":
            return E.consume_poison(cmd[1], character, do_print)
        case "wait_time":
            return E.wait_time(character, False)
        case "make_poisoned_coffee":
            return E.make_poisoned_coffee(character, do_print)
        case "consume_inedible":
            return E.consume_inedible(cmd[1], character, do_print)
        case "give_coffee_or_poison":
            return E.give_coffee_or_poison(cmd[1], cmd[3], character, do_print)
        case "give_obj":
            return E.give_obj(cmd[1], cmd[3], character, do_print)
        case "email_work":
            return E.email_work(character, do_print)
        case "talk_to":
            return E.talk_to(cmd[1], character, do_print)
        case "drink_medicine":
            return E.drink_medicine(cmd[1], character, do_print)
        case "help_command":
            return P.help_command(do_print)
        case "give_cake":
            return E.give_cake(cmd[1], cmd[3], character, do_print)
        case "consume_cake":
            return E.consume_cake(cmd[1], character, do_print)
        case _:
            return False


def player_action(character: objUID, P: Parser, E: Events):
    global unparsed_cmd

    # DEBUG #
    # cmd = [None,None,None,None]
    # do_action("wait_time", cmd, character, P, E)  # player just waits every turn

    valid_action = False
    while not valid_action:
        unparsed_cmd = input("> ")
        if unparsed_cmd in ["Q", "q", "quit", "skip day"]:
            break

        cmd = P.parse_input(unparsed_cmd)
        subroutine_key = P.find_subroutine_call(cmd)

        print(f"DEBUG cmd: {cmd}")
        print(f"DEBUG subroutine_key: {subroutine_key}")

        verb_str = (
            P.get_back_the_verb_string(int(cmd[0]), unparsed_cmd)
            if cmd[0] is not None
            else None
        )
        valid_action = do_action(subroutine_key, cmd, character, P, E, verb_str, True)


def random_action(npc_character: objUID, P: Parser, E: Events):
    valid_action = False
    while not valid_action:
        rand_action = rnd.choice(list(P["lookup_table"]))
        cmd = rand_action[:4]
        subroutine_key = rand_action[4]
        rand_obj1 = rnd.choice(list(P["game_dictionary"]))
        rand_obj2 = rnd.choice(list(P["game_dictionary"]))
        if cmd[1] == "*":
            cmd[1] = rand_obj1
        if cmd[3] == "*":
            cmd[3] == rand_obj2

        # DEBUG #
        # print(f"cmd: {cmd}")
        # print(f"subroutine_key: {subroutine_key}")

        valid_action = do_action(subroutine_key, cmd, npc_character, P, E)

    print(
        f"I do: {list(P["verbs"][str(cmd[0])])[0]} {cmd[1] if cmd[1] is not None else ""} {cmd[2] if cmd[2] is not None else ""} {cmd[3] if cmd[3] is not None else ""}"
    )


def character_action(character: objUID, P: Parser, E: Events):
    if E.O.get_character_data("uses_parser", character):
        player_action(character, P, E)
    else:
        random_action(character, P, E)


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
    print("NONE OF YOU GOT THE BOSS'S FAVOUR")
    print("YOU ALL DID A BAD JOB IN THE INTERNSHIP")
    print('"PROFESSIONALS YOU ARE NOT" WAS THE')
    print("BOSS'S LASTS WORDS TO ALL OF YOU!!!")


# INSIDE Events aka E.power_down()
# can be called from spill_coffee
def power_down(turns=10):
    E["variables"]["is_lights_out"] = True
    E["variables"]["remaining_lights_out"] = turns
    for obj, attr in O.items():
        if O.is_valid_obj(obj):
            room = O.get_holder(obj)
            if O.get_obj_type(obj) == "character":
                O.change_holder(obj, room, "electrical_room")


def electric_shutdown():
    print("###########")
    print("#  EVENT  #")
    print("###########")
    print()
    msvcrt.getch()
    print("******** ELECTRIC SHUTDOWN ********")
    print()
    msvcrt.getch()
    print("THE LIGHTS SUDDENLY WENT DOWN")
    msvcrt.getch()
    print('BOSS: "GO FIX THE BREAKER YOU USELESS INTERNS!!!"')
    msvcrt.getch()
    print()
    print("Everyone hurried to the electric room")
    msvcrt.getch()
    print("as per the boss's orders. Fix the lights")
    msvcrt.getch()
    print("or take opportunity of the situation...")
    msvcrt.getch()
    print()
    print("**********************************************")
    print()
    power_down(25)
    msvcrt.getch()
    pass


def check_power():
    if E["variables"]["remaining_lights_out"] > 0:
        E["variables"]["remaining_lights_out"] = (
            E["variables"]["remaining_lights_out"] - 1
        )
        if E["variables"]["remaining_lights_out"] == 0:  # <= 0
            print("THE LIGHTS ARE BACK ON!")
            print()
            E["variables"]["is_lights_out"] = False


likability_goal = 80
friendliness_goal = 5


def ending_result():
    global likability_goal, friendliness_goal, characterS
    friendliness_reached = True
    likability_reached = [True] * len(characterS)
    likability_reached_idxS = []
    pitcher = None
    for i, character in enumerate(characterS):
        current_friendliness = E.O.get_character_data("friendliness", character)
        if (
            current_friendliness is not None
            and current_friendliness < friendliness_goal
        ):
            friendliness_reached = False
        if E.O.get_character_data("likability", character) < likability_goal:
            likability_reached[i] = False
    for i, b in enumerate(likability_reached):
        if b:
            likability_reached_idxS.append(i)
    if len(likability_reached_idxS) > 0:
        pitcher = characterS[likability_reached_idxS[0]]
        highest_likability = characterS[likability_reached_idxS[0]]
        for i in likability_reached_idxS[1:]:
            if characterS[i] == "player":
                pitcher = "player"
            current_likability = E.O.get_character_data("likability", characterS[i])
            if current_likability > E.O.get_character_data(
                "likability", highest_likability
            ):
                highest_likability = characterS[i]

    # ending 1
    if friendliness_reached and any(likability_reached):
        return job_offer_with_coworker(E.O.get_character_data("name", pitcher))
    # ending 2
    if any(likability_reached):
        return exclusive_job_offer(E.O.get_character_data("name", highest_likability))
    # ending 3
    if not any(likability_reached):
        return no_one_gets_rehired()


E.greet_at_game_start("player")

t = 0.1
game_day = 5
turns_in_a_day = 45
ANNIVERSARY_DAY = 1 #5
ELECTRIC_SHUTDOWN_DAY = 2#3

characterS = []
for obj in O.keys():
    if E.O.get_obj_type(obj) == "character":
        characterS.append(obj)

unparsed_cmd = None  # input("> ")  # e.g. `> put A LaXaTiVe in the coffee`
# while game_day > 0 and unparsed_cmd not in ["Q", "quit"]: #while not ending():
for day in range(1, game_day + 1):
    skip_day = False
    print("#########")
    print(f"# DAY {day} #")
    print("#####################################################################")
    for turn in range(turns_in_a_day):
        if day == ELECTRIC_SHUTDOWN_DAY and turn == 2: #10:
            electric_shutdown()
        if day == ANNIVERSARY_DAY and turn == 2: #20:
            E.boss_anniversary()
        for character in characterS:
            print(f"{character.upper()} TURN")
            print("*************************************")
            skip_turn = E.O.get_character_data("skip_turn", character)
            turn_speed = E.O.get_character_data("turn_speed", character)
            # DEBUG #
            # print(f"DEBUG {character} skip_turn: {skip_turn}")
            # print(f"DEBUG {character} turn_speed: {turn_speed}")
            print(f"holder: {E.O.get_holder(character)}")
            print(f"holding: {E.O.get_holding(character)}")
            print(f"likability: {E.O.get_character_data("likability", character)}")
            print(f"friendliness: {E.O.get_character_data("friendliness", character)}")
            print("------------")
            if skip_turn > 0:
                print("skipping turn...")
                print(f"because {E.O.get_character_data("skip_cause", character)}")
                # if character == "player":
                #     print("skipping turn...")
                #     print(f"because {E.O.get_character_data("skip_cause", character)}")
                skip_turn -= 1
                E.O.set_character_data(character, "skip_turn", skip_turn)
            else:
                if rnd.randint(1, 100) <= turn_speed:
                    character_action(character, P, E)
                else:
                    print("You are unwell and lost the turn")  # DEBUG
                if turn_speed > 100 and rnd.randint(1, 100) <= turn_speed - 100:
                    print("(extra turn granted caffinated or sugar rush in effect)")
                    # if character == "player":
                    #     print("(extra turn granted) caffinated in effect...")
                    character_action(character, P, E)  # see extra action
            print("*************************************\n")

            if character == "player":
                msvcrt.getch()

            # sleep(t)

            if unparsed_cmd in ["Q", "q", "quit"]:
                break
            if unparsed_cmd == "skip day":
                skip_day = True
                break
        else:  # aka is nobreak
            check_power()
            continue
        break
    else:  # aka is nobreak
        # go_home()  # prints go home OR even another function just being home doing things at home for some turns
        print("ITS TIME TO GO HOME")
        print("say bye to everyone")
        input("> ")
        print()
        continue
    if skip_day:
        skip_day = False
        print("You skipped the day! now what?\n")
        continue
    break

ending_result()  # show the result based on all stats
if unparsed_cmd in ["Q", "q", "quit"]:
    os.abort()
print()
print("YOU FINISHED THE GAME!")
print("CONGRATULATIONS!!!")
print(
    """
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
"""
)


# checked_likability = []
# def check_milestone():
#   if any likability == 50:
#     print(f"{character_x} has reached good boss connections")
#     checked_likability.append(character_x)


# USING percentage of having a chance to move per turn
world_speed = 70  # 100 is default, 120 is energized, 70 is poisoned
skip_npc_turn = 0  # skips turn due to some event e.g. spilled coffee
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
player_speed = 7
npc_speed = 10  # 0.7:1 ratio  //poisoned
# for _ in range(player_speed):
# 	player_action()
# for _ in range(npc_speed):
# 	npc_action()
