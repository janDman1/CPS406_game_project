from utils import delay, dotdotdot
import random as rnd

type objUID = str

class SabotageAction:
    
    def karateyd(
        self, verb: str, obj: objUID, character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        room_characterS = [
            o
            for o in room_holdings
            if self.O.get_obj_type(o) in ["character", "static_chracter"]
            and o != character
        ]
        if obj == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            obj = "poisoned_coffee"
        # either the valid obj name "room" or specified the actual room the character is in e.g. "cafeteria" can both be used
        if obj == "room" or obj == room:
            if do_print:
                print(f"you punched a wall in the {room}")
                dotdotdot(False)
                print("OUCH!")
                delay()
                print("That hurts.")
                delay()
                print("You came to your senses.")
                print("Im never punching a wall again.")
            return True
        map_obj_name = self.map_to_actual_obj(obj, character)
        if map_obj_name != "no obj found":
            obj = map_obj_name
        obj_type = self.O.get_obj_type(obj)

        original_obj = obj

        if self["variables"]["is_boss_anniversary"] and obj == "boss":
            if do_print:
                print("I LIKE HOW YOU HIT BOI!!!")
                delay()
                print("HERE'S MY DAUGHTER!")
            self["variables"]["is_a_secret_endings"]["marry_daughter"] = True
            return True

        if self["variables"]["is_lights_out"] and "flashlight" not in char_inventory:
            if obj != character:  # if you are not punching yourself
                obj_is_a_character = obj_type in ["character", "static_character"]
                if obj_is_a_character:
                    victim_name = self.O.get_character_data("name", original_obj)
                if obj not in char_inventory or obj_is_a_character:
                    if do_print:
                        print(
                            f"You {"fling your arm" if verb == "punch" else "ready your feet"} to try to {verb} {victim_name if obj_is_a_character else original_obj}",
                            end="",
                        )
                        dotdotdot()

                if obj_is_a_character:
                    if len(room_characterS) > 0:
                        obj = rnd.choice(room_characterS)
                        victim_name = self.O.get_character_data("name", obj)
                        if obj == original_obj:
                            if do_print:
                                print("and you actually hit your target!")
                        else:
                            if do_print:
                                print(
                                    f"but you hit {victim_name} instead!"
                                )  # somebody else
                        # falls through for character hit dialogue and item drop
                    else:
                        if do_print:
                            print("until you noticed there was actually no one there")
                            print(f"You've been {verb}ing air this whole time!")
                        return True

                elif obj not in char_inventory:
                    if do_print:
                        print(
                            f"Is {victim_name if obj_type in ["character","static_character"] else original_obj} even there?"
                        )
                        print("I can't really see anything")
                    return True

        if obj_type == "room":
            if do_print: print("go to that room to throw your tantrum")
            return False  # can't kick or throw tantrum in another room
        if obj_type == "item":
            if obj in room_holdings or obj in char_inventory:
                coffee_types = ["coffee", "poisoned_coffee"]
                if obj in coffee_types:
                    if do_print:
                        print("you broke the mug, ", end="")
                        delay()
                        print("hurt yourself, ", end="")
                        delay()
                        print("and spilled coffee", end="")
                        dotdotdot()
                        print("*good job*")
                        delay()
                    where_coffee_at = (
                        room
                        if any(item in room_holdings for item in coffee_types)
                        else (
                            character
                            if any(item in char_inventory for item in coffee_types)
                            else None
                        )
                    )
                    if where_coffee_at is not None:
                        self.O.remove_holding(obj, where_coffee_at)
                elif obj == "cabinet":
                    if do_print:
                        print("You punched the cabinet", end="")
                        dotdotdot()
                        print("and broke your fingers! ouch!")
                        delay()
                        print("But as the cabinet breaks into pieces you see something suspicious behind it")
                    self.O.add_holding("broken_cabinet", "boss_office")
                    self.O.remove_holding("cabinet", "boss_office")

                    return True

                else:
                    if do_print:
                        print("uhh", end="")
                        dotdotdot()
                        print("no thank you")
                        delay()
                return False
            else:
                if do_print:
                    print(
                        "You can't see that"
                    )  # --------------------------------------------------------------- maybe mistake
                return False
        if obj_type == "character":
            victim_name = self.O.get_character_data("name", obj)
            inventory = self.O.get_holding(obj)
            dropped_item = rnd.choice(inventory) if len(inventory) != 0 else None
            current_friendliness = self.O.get_character_data("friendliness", obj)

            if obj in self.O.get_holding(room):
                if do_print:
                    if obj == character:
                        print("Ughh, I hate myself!")
                        print("What is wrong with me!")
                        print(f"You {verb} yourself")
                        print(
                            f"You stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}"
                        )
                    else:
                        print(f"You {verb} {victim_name}", end="")
                        dotdotdot()

                        print(
                            f"{victim_name} stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}"
                        )
                        delay()
                        print(f'"shit man!"')
                        delay()
                        print(f"{victim_name} gets up, and brushes you off")
                        delay()
                        print(f"Friendliness with {victim_name} decreased")

                if dropped_item is not None:
                    self.O.change_holder(dropped_item, obj, room)
                    if (
                        self.O.get_character_data("uses_parser", character)
                        and obj != character
                    ):
                        self.O.set_character_data(
                            obj, "friendliness", current_friendliness - 1
                        )

                return True
            else:
                if do_print:
                    print(f"{victim_name} isn't even there dummy")
                return False

        if obj_type == "static_character" and obj in self.O.get_holding(room):
            victim_name = self.O.get_character_data("name", obj)
            if do_print:
                print(f"Im scared to {verb} {victim_name}, they might report me")

        return False
    

    def thrown_obj_at_x(self, thrown_obj:objUID, thrown_to:objUID, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        current_likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)

        # map to synonmys to use plus verify
        thrown_obj = self.map_to_actual_obj(thrown_obj, character)
        if thrown_obj == "no obj found":
            if do_print: print(f"{thrown_obj} is not in the game dictionary")
            return False
        thrown_to = self.map_to_actual_obj(thrown_to, character)
        if thrown_to == "no obj found":
            if do_print: print(f"{thrown_to} is not in the game dictionary")
            return False
        obj_type = self.O.get_obj_type(thrown_obj)
        thrown_to_type = self.O.get_obj_type(thrown_to)
        
        # valid objects to throw and person to throw to
        if obj_type != "item":
            if do_print:
                print(f"How would you even throw that", end="")
                self.symsymsym("?")
            return False
        if thrown_to_type not in ["character", "static_character"]:
            if do_print: 
                print("What even would be the point of that", end="")
            return False
        victim_name = self.O.get_character_data("name", thrown_to)
        
        if thrown_obj not in inventory:
            if do_print: print("Maybe try finding the item first, that would be smart.")
            return False
        if thrown_to not in self.O.get_holding(room):
            if do_print: print(f"Maybe try finding {victim_name} first, that would be smart")
            return False
        if thrown_to_type == "character":
            if do_print:
                print(f"{victim_name} Ouch! why did you that!!")
                print(f"Friendliness with {victim_name} decreased")
            current_friendliness = self.O.get_character_data("friendliness", thrown_to)
            self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        if thrown_to_type == "static_character":
            if thrown_to == "boss":
                if do_print:
                    print(f"{victim_name} Bold strategy, I'm deducting 50 percent of your salary!")
                    delay()
                    print("your likabity to boss decreased")
                current_likability = self.O.get_character_data("likability", character)
                self.O.set_character_data(character, "likability", current_likability - 15)
            else:
                if do_print:
                    print("Wow did you really do that")
                    delay()
                    print("Just so you know, I know where you live")
                    delay()
                    print(f"Friendliness with {victim_name} decreased")
                current_friendliness = self.O.get_character_data("friendliness", thrown_to)
                self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        self.O.change_holder(thrown_obj, character, room)
        return True

   
    def hack_computer(self, destination: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        inventory = self.O.get_holding(character)
        LIKABILITY_CUT = 8

        if "usb_hacking_script" in inventory and room == "offices" and destination in ["workstation_1", "workstation_2", "workstation_3"]:
            if do_print:
                print("You insert the USB hacking script into the computer.")
                delay()
                print("The computer starts running the script...")
                delay(3)
            if destination == "workstation_1":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 1.")
                    print(f"{self.O.get_character_data("name", "player")} lost {LIKABILITY_CUT} likability for")
                player_likability = self.O.get_character_data("likability", "player")
                self.O.set_character_data("player", "likability", player_likability - LIKABILITY_CUT)
            elif destination == "workstation_2":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 2.")
                    print(f"{self.O.get_character_data("name", "NPC_1")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as his background.")
                philp_likability = self.O.get_character_data("likability", "NPC_1")
                self.O.set_character_data("NPC_1", "likability", philp_likability - LIKABILITY_CUT)
            elif destination == "workstation_3":
                if do_print: 
                    print("Access granted! You successfully hacked workstation 3.")
                    print(f"{self.O.get_character_data("name", "NPC_2")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as her background.")
                serah_likability = self.O.get_character_data("likability", "NPC_2")
                self.O.set_character_data("NPC_2", "likability", serah_likability - LIKABILITY_CUT)
            return True
        else:
            if "usb_hacking_script" not in inventory:
                if do_print: print("You need the USB hacking script to perform this action.")
            if room != "offices":
                if do_print: print("You need to be in the offices to hack the computer.")
            return False
    

    def make_poisoned_coffee(self, character: objUID, do_print=True) -> bool:
        # maybe make it work later for coffee in the room
        if all(x in self.O.get_holding(character) for x in ["coffee", "laxative"]):
            if do_print:
                print("Lacing coffee with poison muwahaha!")
                delay()
                print("Done")
            self.O.remove_holding("coffee", character)
            self.O.remove_holding("laxative", character)
            self.O.add_holding("poisoned_coffee", character)
            return True
        if do_print:
            print("I need to be holding both items")
        return False
    

    def give_coffee_or_poison(
        self, obj: objUID, to_character: objUID, from_character: objUID, do_print=True
    ) -> bool:
        room = self.O.get_holder(from_character)
        to_character = self.map_to_actual_obj(to_character, from_character)
        inventory = self.O.get_holding(from_character)

        if self.O.get_obj_type(to_character) not in ["character", "static_character"]:
            if do_print:
                print(f"Giving to a {to_character}, are you mad?")
            return False
        gifted_name = self.O.get_character_data("name", to_character)
        current_friendliness = self.O.get_character_data("friendliness", to_character)
        if obj == "coffee" and "poisoned_coffee" in inventory:  # + room_holdings
            obj = "poisoned_coffee"
        if obj in inventory:
            if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
                if do_print:
                    print("You cannot see anyone in this darkdness")
                    delay()
                    print("but im sure they'd like a warm coffee to wait it out")
                return False
            if to_character in self.O.get_holding(room):
                spotted = rnd.randint(1, 100) <= 30
                if (
                    obj == "poisoned_coffee" and spotted
                ):  # 30% chance of getting spotted if giving poisoned coffee
                    if do_print:
                        print("You think I'd fall for it!")
                        delay()
                        print("I know you are handing me a poisoned coffee")
                        delay()
                        print(f"Friendliness with {gifted_name} decreased")
                    # positive
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(
                            to_character, "friendliness", current_friendliness - 1
                        )
                else:
                    if do_print:
                        print(f"{gifted_name}: Thanks for the coffee!")
                        delay()
                        print(f"Friendliness with {gifted_name} increased")
                    # negative
                    if self.O.get_character_data("uses_parser", from_character):
                        self.O.set_character_data(
                            to_character, "friendliness", current_friendliness + 1
                        )
                self.O.change_holder(obj, from_character, to_character)
                return True
            else:
                if do_print:
                    print(f"{gifted_name} isn't here go look for em")
        else:
            if do_print:
                print(f"I need to get more coffee before that")
        return False


    def drink_medicine(self, obj, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj in inventory:
            if self.O.get_character_data("turn_speed", character) < 100:
                if do_print:
                    print("I drink medicine, now I feel good")
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 100)  # make healthy
                return True
            else:
                if do_print:
                    print("Why? You are perfectly healthy")
                return False
        if do_print:
            print("You don't have item!")
        return False
    
    