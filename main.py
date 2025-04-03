# from events import Events
from all_actions import Actions as Events
from obj_dict import ObjDict
from parser import Parser
from utils import remove_comments

import json
import random as rnd
import os
import msvcrt


"""
RETURN OFFER RUSH GAME

"""

#### GAME RUN ####

## INITIALIZE ##


# LOAD DATA FILE AS YOUR DATABASE TO USE
# parsed_data_file = remove_comments(open("data.txt").read())
parsed_data_file = remove_comments(open("data.txt").read())
All_Data = json.loads(parsed_data_file)

O = ObjDict(All_Data["Objects"])
# adds to Objects data while game is running
# O["snacks"] = {
#     "type": "item",
#     "holder": "cafeteria",
#     "description": "Something to temporary fill the hunger.",
#     "attributes": ["energize"],
# }
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
        case "place_obj":
            return E.place_obj(cmd[1], cmd[3], character, do_print)
        case "hack_computer":
            return E.hack_computer(cmd[1], character, do_print)
        case "take_from_container" :
            return E.take_from_container(cmd[1], cmd[3], character, do_print)
        case "thrown_obj_at_x":
            return E.thrown_obj_at_x(cmd[1], cmd[3], character, do_print)
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

        if subroutine_key == "no match":
            print("the stock market gods are baffled by your input")
            print("learn how to spell. Use [ > help ]!!!")

        # print(f"DEBUG cmd: {cmd}")
        # print(f"DEBUG subroutine_key: {subroutine_key}")

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
    msvcrt.getch()
    print("EVEN THOUGHT SOME OF YOU DID'T GET THE BOSS'S")
    msvcrt.getch()
    print(f"FAVOUR, {pitcher.upper()} PITCHED IN FOR Y'ALL!")
    msvcrt.getch()

def exclusive_job_offer(highest_likability):
    print("OUTSMARTING AND OUTPERFORMING THEIR RIVALS WITH A MIX OF SKILL,") 
    msvcrt.getch()
    print("CHARM, AND A LITTLE BIT OF QUESTIONABLE ETHICS!") 
    msvcrt.getch()
    print("THE BATTLE FOR SUPREMACY RAGED ON FROM DAY ONE,") 
    msvcrt.getch()
    print("BUT ONE, ONLY ONE STOOD ON TOP! THAT IS")
    msvcrt.getch()
    print(f"{highest_likability.upper()} BEAT EVERYONE IN CAPABILITIES")
    msvcrt.getch()

def no_one_gets_rehired():
    print("NONE OF YOU GOT THE BOSS'S FAVOUR")
    msvcrt.getch()
    print("YOU ALL DID A BAD JOB IN THE INTERNSHIP")
    msvcrt.getch()
    print("PROFESSIONALS YOU ARE NOT WAS THE")
    msvcrt.getch()
    print("BOSS'S LASTS WORDS TO ALL OF YOU!!!")
    msvcrt.getch()
    print("BUT I HEARD MCDONALDS IS HIRING")

def become_a_millionaire():
    print("They all said you were crazy.")
    msvcrt.getch()
    print("They all said to sell.")
    msvcrt.getch()
    print("\"Crypto's just a fad!\" they laughed.")
    msvcrt.getch()
    print("\"Invest in something real!\" they scoffed.")
    msvcrt.getch()
    print("But look at them now.")
    print()
    msvcrt.getch()
    print("You did not even bother checking if you got the return offer. You did not even need the boss's approval. You just needed Intern Coin the next big thing that everyone doubted. While they are still grinding away at office politics, you are floating on your private yacht, sipping champagne with a smug grin.")
    print()
    msvcrt.getch()
    print("Now you can brag to your homeless friends about their poverty while you live it up using your big boy bucks to buy stupid things like a gold-plated suitcase.")
    print()
    msvcrt.getch()
    print("Congratulations! You beat the game by skipping the corporate nonsense and going straight to billionaire status. Who needs a job when you are too busy buying the entire company?")
    print()
    msvcrt.getch()

def become_boss():
    print("SECERT ENDING FOUND!!!!\n\nYou finally did it. After countless hours of digging, snooping, and dodging coffee attacks from your rivals, you uncovered the truth: the boss has been laundering company money like a washed-up mobster with a taste for 'consulting fees.' Armed with undeniable evidence and a flair for the dramatic, you waltzed straight into the board meeting with Steve Jobs and dropped the bombshell.\n")
    msvcrt.getch()
    print("The fallout was glorious. The boss was escorted out in handcuffs, sputtering excuses about 'creative accounting' and 'spiritually motivated investments.' The board was so impressed with your bravery and sheer audacity that they offered you his position on the spot.\n")
    msvcrt.getch()
    print("Now you're the boss. The office trembles at your presence. Your rivals are nothing but distant memories, and your new empire is built on the ashes of your former employer's downfall. You're rich beyond your wildest dreams and can now hire your own army of interns to do your bidding or just throw coffee at each other for your amusement.\n")
    msvcrt.getch()
    print("The best part? You never have to worry about impressing anyone ever again. You are the corporate overlord now.\n")
    msvcrt.getch()
    print("Congratulations! You played the game, beat the boss, and became the legend. Enjoy ruling with a coffee mug in one hand and the power to ruin lives in the other.\n")
    msvcrt.getch()

def marry_daughter():
    print("SECERT ENDING FOUND!!!!\n\nYou did it! You got the job offer, and as if that wasn't enough, you somehow managed to charm your way into a relationship with the boss's daughter.")
    msvcrt.getch()
    print("Now you get to sit back, kick your feet up, and watch the money roll in while your new sugar mama takes care of everything. The best part? You do not even have to worry about impressing the boss anymore you're practically family.")
    msvcrt.getch()
    print("Who knew that your internship would end in both professional success and romantic bliss? Some might call it luck, others might call it pure genius. Either way, you have made it, and life just got a whole lot easier.")
    msvcrt.getch()
    print("Congratulations! You’ve officially secured both the job and a lifelong supply of luxury coffee and designer clothes. Enjoy your new life as the ultimate corporate gold digger!")
    msvcrt.getch()

def print_ending_frame():
    print("""
          )   (       (         )             
       ( /(   )\ )    )\ )   ( /(   (         
 (     )\()) (()/(   (()/(   )\())  )\ )      
 )\   ((_)\   /(_))   /(_)) ((_)\  (()/(      
((_)   _((_) (_))_   (_))    _((_)  /(_))_    
| __| | \| |  |   \  |_ _|  | \| | (_)) __|   
| _|  | .` |  | |) |  | |   | .` |   | (_ |   
|___| |_|\_|  |___/  |___|  |_|\_|    \___|   
""")
    print()
    msvcrt.getch()

def ending_result():
    global LIKABILITY_GOAL, FRIENDLINESS_GOAL, characterS
    friendliness_reached = True
    likability_reached = [True] * len(characterS)
    likability_reached_idxS = []
    pitcher = None
    for i, character in enumerate(characterS):
        current_friendliness = E.O.get_character_data("friendliness", character)
        if (
            current_friendliness is not None
            and current_friendliness < FRIENDLINESS_GOAL
        ):
            friendliness_reached = False
        if E.O.get_character_data("likability", character) < LIKABILITY_GOAL:
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

    # ending 4
    if "intern_coin" == E.O.get_holding("player"):
        return 
    # ending 1
    if friendliness_reached and any(likability_reached):
        return job_offer_with_coworker(E.O.get_character_data("name", pitcher))
    # ending 2
    if any(likability_reached):
        return exclusive_job_offer(E.O.get_character_data("name", highest_likability))
    # ending 3
    if not any(likability_reached):
        return no_one_gets_rehired()

def check_secret_ending() -> bool:
    for k,v in E["variables"]["is_a_secret_endings"].items():
        if v:
            print_ending_frame()
            if k == "become_boss":
                become_boss()
            if k == "marry_daughter":
                marry_daughter()
            return True
    return False           

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
    power_down(POWER_DOWN_DURATION)
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

E.greet_at_game_start("player")

t = 0.1
GAME_DAYS = 5
TURNS_IN_A_DAY = 30
ANNIVERSARY_DAY = 5
ELECTRIC_SHUTDOWN_DAY = 3
INSPECTION_DAY = 2
POWER_DOWN_DURATION = 25 #30
LIKABILITY_GOAL = 80
FRIENDLINESS_GOAL = 20

characterS = []
for obj in O.keys():
    if E.O.get_obj_type(obj) == "character":
        characterS.append(obj)

unparsed_cmd = None  # input("> ")  # e.g. `> put A LaXaTiVe in the coffee`
# while GAME_DAYS > 0 and unparsed_cmd not in ["Q", "quit"]: #while not ending():
for day in range(1, GAME_DAYS + 1):
    skip_day = False
    print("#########")
    print(f"# DAY {day} #")
    print("#####################################################################")
    for turn in range(TURNS_IN_A_DAY):
        if day == ELECTRIC_SHUTDOWN_DAY and turn == 2: #10:
            electric_shutdown()
        if day == ANNIVERSARY_DAY and turn == 5: #20:
            E.boss_anniversary()
        if day == INSPECTION_DAY and turn == 8:
            E.boss_inspection()
        for character in characterS:
            character_name = E.O.get_character_data("name", character)
            print(f"{character_name.upper()}'S TURN")
            print("*************************************")
            skip_turn = E.O.get_character_data("skip_turn", character)
            turn_speed = E.O.get_character_data("turn_speed", character)
            # DEBUG #
            # print(f"DEBUG {character} skip_turn: {skip_turn}")
            # print(f"DEBUG {character} turn_speed: {turn_speed}")
            # print(f"holder: {E.O.get_holder(character)}")
            # print(f"holding: {E.O.get_holding(character)}")
            if character != "player":
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

            if check_secret_ending(): break

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

if unparsed_cmd in ["Q", "q", "quit"]:
    os.abort()
if E.is_secret_ending() == "no secret endings met":
    print_ending_frame()
    ending_result()  # show the result based on all stats
print()
print("YOU FINISHED THE GAME!")
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
