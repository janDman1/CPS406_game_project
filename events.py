from base_actions import Actions
from utils import delay, dotdotdot
import msvcrt
import random as rnd
type objUID = str


class Events(Actions):
    
    def boss_inspection(self):
        contraband = ["laxative", "poisoned_coffee", "usb_hacking_script", "fake_resume", "suspicious_document"]

        """
        teleport everyone to office
        check each table of the people
        if person has their likability goes down?
        or get fired?

        """

        print("###########")
        print("#  EVENT  #")
        print("###########")
        print()
        msvcrt.getch()
        print("******** INSPECTION DAY ********")
        print()
        msvcrt.getch()
        print("The boss shouts from the office!")
        print()
        msvcrt.getch()
        print("BOSS: YOU MAGGOTS!")
        msvcrt.getch()
        print("TO THE WORKSTATIONS IMMEDIATELY!!!")
        msvcrt.getch()
        print()
        msvcrt.getch()
        print("everyone lines up in the offices room")
        msvcrt.getch()
        print("he looks at each of your tables")
        msvcrt.getch()
        print()
        print("you gulp as he inspects veery closely", end="")
        dotdotdot()
        msvcrt.getch()
        print()
        print("**********************************************")
        print()
        msvcrt.getch()

        for obj in self.O.keys():
            if self.O.get_obj_type(obj) == "character":
                # teleports players to offices for the event
                room = self.O.get_holder(obj)
                self.O.change_holder(obj, room, "offices")
                name = self.O.get_character_data("name", obj)

                if obj in ["player", "NPC_1", "NPC_2"]:
                    current_likability = self.O.get_character_data("likability", obj)
                    character_station = "workstation_1" if obj == "player" else "workstation_2" if obj == "NPC_1" else "workstation_3"
                    for item in self.O.get_holding(obj) + self.O.get_holding(character_station):
                        if item in contraband:
                            print(f"{name} why do you have {item}??")
                            delay()
                            print(f"Are you trying to destroy the professionality")
                            delay()
                            print("of our establishment!!")
                            delay()
                            print("likability decreased")
                            print()
                            self.O.set_character_data(obj, "likability", current_likability - 5)
                            break
                    else:
                        if obj == "player":
                            print(f"{name}, You are a good boi!")
                        else:
                            print(f"great job {name}")
                        delay()
                        print("likability increased")
                        print()
                        self.O.set_character_data(obj, "likability", current_likability + 5)
        print()
    
    def give_cake(self, obj, taker:objUID, giver:objUID, do_print=True):
        cake_list = ["strawberry_cake","vanilla_cake","chocolate_cake"]
        
        # get the right cake by manual check
        if obj == "cake":
            for cake in cake_list:
                if cake in self.O.get_holding(giver):
                    obj = cake

        # map the rest of synonyms
        mapped_obj = self.map_to_actual_obj(obj, giver)
        if mapped_obj == "no obj found":
            # shouldn't be possible but just in case
            if do_print:
                print("You are trying to give something that does not exist")
            return False
        else: obj = mapped_obj
        
        # maps name to actual obj for characters
        taker = self.map_to_actual_obj(taker, giver)
        taker_type = self.O.get_obj_type(taker)
        if taker_type not in ["character", "static_character"]:
            if do_print: print(f"You cannot give to a {taker}")
            return False
        taker_name = self.O.get_character_data("name", taker)

        # giver will always be a valid character so no need to verify
        room = self.O.get_holder(giver)
        inventory = self.O.get_holding(giver)
        current_likability = self.O.get_character_data("likability", giver)

        if obj not in inventory:
            if do_print: print("I need to get cake first")
            return False

        # i.e. if giver is a "player"
        if self.O.get_character_data("uses_parser", giver):
            if taker == "boss":
                if "boss" not in self.O.get_holding(room):
                    print("Go look for the boss first")
                    return False

                # NPCs will give their cake then falls through to give your cake
                # but they can drop the cake or you can steal them anytime
                else:
                    cake_list = [x for x in cake_list if x not in self.O.get_holding("player")]
                    # maybe just adjusting NPC likability once given
                    # npc = f"NPC_{i}"
                    # npc_likability = self.O.get_character_data("likability", npc)
                    # self.O.set_character_data(npc, "likability", npc_likability + 5)
                    for i,cake in enumerate(cake_list,1):
                        self.give_cake(cake, "boss", f"NPC_{i}", False)

        if taker == "boss":
            if obj == "chocolate_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability + 20
                )
                if do_print:
                    print(f"{taker_name}: I love chocolate cake! You're the best!")
            if obj == "strawberry_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability + 2
                )
                if do_print:
                    print(f"{taker_name}: I like chocolate more, but thank you!")
            if obj == "vanilla_cake":
                self.O.remove_holding(obj, giver)
                self.O.set_character_data(
                    giver, "likability", current_likability - 10
                )
                if do_print:
                    print(f"{taker_name}: I HATE VANILLA CAKE! GET OUT OF MY SIGHT!")
            return True
        else:
            if taker in self.O.get_holding(room):
                if do_print: print("I'm sure the boss will like it better")
            else:
                if do_print: 
                    print(f"{taker_name} isn't in the room")
                    delay()
                    print(f"but should you really give to {taker_name}?")
            return False

    def greet_at_game_start(self, character) -> None:
        print(
            """
         _____      _                       ____   __  __            _____           _    
        |  __ \    | |                     / __ \ / _|/ _|          |  __ \         | |    
        | |__) |___| |_ _   _ _ __ _ __   | |  | | |_| |_ ___ _ __  | |__) |   _ ___| |__  
        |  _  // _ \ __| | | | '__| '_ \  | |  | |  _|  _/ _ \ '__| |  _  / | | / __| '_ \\
        | | \ \  __/ |_| |_| | |  | | | | | |__| | | | ||  __/ |    | | \ \ |_| \__ \ | | |
        |_|  \_\___|\__|\__,_|_|  |_| |_|  \____/|_| |_| \___|_|    |_|  \_\__,_|___/_| |_| """
        )

        delay(2)

        print(
            """
--------------------------------------------------------------------------------------------------------
                                              STORY
             


As a new intern at Pentagon Inc., you must secure a return offer by currying favour with your boss. 
Compete against two other interns in this cutthroat corporate environment, using clever tactics and 
collected items to gain the upper hand. Build relationships, sabotage rivals, and manipulate 
situations to boost your standing. Use whatever means at your disposal to get the full-time position 
as the job market is tough and you will never again have a job.


"""
        )
        delay(3)
        print("""
----------------------------------------------------------------------------------------------------------
                                             OBJECTIVE


                       
Secure a return job offer by earning the boss's favour
Undermine rival interns using creative sabotage or forge friendships by working together
Explore the map and collect useful items to gain advantages
Discover hidden secrets and unlock unique endings
             
             
----------------------------------------------------------------------------------------------------------
"""
        )

        delay(3)
        print(self["event_dialogues"]["greet_at_game_start"])
        name = input("what is your name? \n> ")
        while name == "":
            print("Please enter a name")
            name = input("what is your name? \n> ")
        room = self.O.get_holder(character)
        self.O.set_character_data(character, "name", name)
        print(f"\nYou were dropped of at the {room}.\n")

    def boss_anniversary(self):
        self["variables"]["is_boss_anniversary"] = True

        # Teleport players
        for obj in self.O.keys():
            if self.O.is_valid_obj(obj) and (
                self.O.get_obj_type(obj) == "character" or obj == "boss"
            ):
                room = self.O.get_holder(obj)
                self.O.change_holder(obj, room, "meeting_room")

        print("###########")
        print("#  EVENT  #")
        print("###########")
        print()
        msvcrt.getch()
        print("******** BOSS ANNIVERSARY PARTY ********")
        print()
        msvcrt.getch()
        print("The old room speaker started ringing for Annoucement")
        msvcrt.getch()
        print("Everyone is to attend this mandatory event for our")
        msvcrt.getch()
        print("beloved Mr.Boss!! You are to leave your workstations")
        msvcrt.getch()
        print("Immediately!!!")
        print()
        msvcrt.getch()
        self.talk_to("boss", "player")
        msvcrt.getch()
        print("There are cakes in the cafeteria")
        msvcrt.getch()
        print("maybe the boss likes some")
        msvcrt.getch()
        print()
        print("**********************************************")
        print()
        msvcrt.getch()

        self.O.add_holding("strawberry_cake", "cafeteria")
        self.O.add_holding("vanilla_cake", "cafeteria")
        self.O.add_holding("chocolate_cake", "cafeteria")
    
    def power_down(self, turns=10):
        self["variables"]["is_lights_out"] = True
        self["variables"]["remaining_lights_out"] = turns
        for obj, attr in self.O.items():
            if self.O.is_valid_obj(obj):
                room = self.O.get_holder(obj)
                if self.O.get_obj_type(obj) == "character":
                    self.O.change_holder(obj, room, "electrical_room")

    def electric_shutdown(self):
        POWER_DOWN_DURATION = 25
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
        self.power_down(POWER_DOWN_DURATION)
        msvcrt.getch()

    def check_power(self):
        if self["variables"]["remaining_lights_out"] > 0:
            self["variables"]["remaining_lights_out"] = (
                self["variables"]["remaining_lights_out"] - 1
            )
            if self["variables"]["remaining_lights_out"] == 0:  # <= 0
                print("=== THE LIGHTS ARE BACK ON! ===")
                print()
                msvcrt.getch()
                self["variables"]["is_lights_out"] = False

    def go_home(self):
        print("ITS TIME TO GO HOME\n")
        msvcrt.getch()
        print("YOU FINISHED YOUR WORK FOR THE DAY")
        delay(1)
        print("THEN TOOK THE USUAL ROUTE BACK HOME")
        delay(1)
        print("EXHAUSTED, ", end="")
        delay(1)
        print("YOU COLLAPSED ON YOUR BED")
        delay(1)
        print("WAKING UP THE NEXT DAY\n")
        delay(1)
        print("TIME TO GO BACK TO WORK\n")
        msvcrt.getch()

    def everything_back_in_place(self):
        container_list = []

        print("You entered the building and now in the main lobby")
        delay(1)
        print("Your fellow interns are already in their workstations")
        delay(1)
        print("and the boss is in his office")
        delay(1)
        print()
        # Teleport characters back to their original rooms, plus the containers
        for obj in self.O.keys():
            if self.O.is_valid_obj(obj):
                obj_type = self.O.get_obj_type(obj)
                room = self.O.get_holder(obj)
                if obj_type == "character":
                    if self.O.get_character_data("uses_parser", obj):
                        self.O.change_holder(obj, room, "main_lobby")
                    else:  # "NPC" in obj:
                        self.O.change_holder(obj, room, "offices")
                if obj == "boss":
                    self.O.change_holder(obj, room, "boss_office")
                
                # check if the object is a container but not a workstation and add it to the list
                if obj_type == "item" and self.O.has_item_attribute("container", obj) and "workstation" not in obj:
                    container_list.append(obj)
        
        # refill items
        coffee_count = self.O.get_holding("cafeteria").count("coffee")
        for i,_ in enumerate(range(5)):
            if coffee_count < 5:
                if i == 0:
                    print("fresh new coffee in the cafeteria")
                self.O.add_holding("coffee", "cafeteria")
                coffee_count += 1
        if "medicine" not in self.O.get_holding("washroom_shelf"):
            print("more medicine in the washroom shelf")
            self.O.add_holding("medicine", "washroom_shelf")
        print("also random laxative spawn!")
        self.O.add_holding("laxative", rnd.choice(container_list+["storage_room"]))
        print()

