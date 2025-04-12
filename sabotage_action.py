from utils import delay, dotdotdot, symsymsym
from base_actions import Actions
import random as rnd
type objUID = str

class SabotageActions(Actions):

    def karateyd(self, verb: str, target: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        room_holdings = self.O.get_holding(room)
        char_inventory = self.O.get_holding(character)
        room_characterS = [
            o
            for o in room_holdings
            if self.O.get_obj_type(o) in ["character", "static_chracter"]
            and o != character
        ]
        if target == "coffee" and "poisoned_coffee" in room_holdings + char_inventory:
            target = "poisoned_coffee"
        # either the valid obj name "room" or specified the actual room the character is in e.g. "cafeteria" can both be used
        if target == "room" or target == room:
            if not self.O.get_character_data("uses_parser", character):
                # NPC never throws tantrum
                return False
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
        
        # map to synonmys to use plus verify
        mapped_obj = self.map_to_actual_obj(target, character)
        if mapped_obj == "no obj found":
            if do_print: print(f"{target} is not in the game dictionary")
            return False
        else: target = mapped_obj
        obj_type = self.O.get_obj_type(target)

        # need copy for obj randomization later i.e. lights out event
        original_target = target

        # EVENTS behaviour change

        if self["variables"]["is_boss_anniversary"] and target == "boss":
            # only a player can get this ending
            if self.O.get_character_data("uses_parser", character):
                if do_print:
                    print("I LIKE HOW YOU HIT BOI!!!")
                    delay()
                    print("HERE'S MY DAUGHTER!")
                self["variables"]["is_a_secret_endings"]["marry_daughter"] = True
                return True
            else:
                return False

        if self["variables"]["is_lights_out"] and "flashlight" not in char_inventory:
            if target != character:  # if you are not punching yourself
                obj_is_a_character = obj_type in ["character", "static_character"]
                if obj_is_a_character:
                    victim_name = self.O.get_character_data("name", original_target)
                if target not in char_inventory or obj_is_a_character:
                    if do_print:
                        print(
                            f"You {"fling your arm" if verb == "punch" else "ready your feet"} to try to {verb} {victim_name if obj_is_a_character else original_target}",
                            end="",
                        )
                        dotdotdot()

                if obj_is_a_character:
                    if len(room_characterS) > 0:
                        target = rnd.choice(room_characterS)
                        victim_name = self.O.get_character_data("name", target)
                        if target == original_target:
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

                elif target not in char_inventory:
                    if do_print:
                        print(
                            f"Is {victim_name if obj_type in ["character","static_character"] else original_target} even there?"
                        )
                        print("I can't really see anything")
                    return True


        if obj_type == "room":
            if do_print: print("go to that room to throw your tantrum")
            return False  # can't kick or throw tantrum in another room
        
        if obj_type == "item":
            if target in room_holdings or target in char_inventory:

                # breaks coffee or poisoned_coffee
                coffee_types = ["coffee", "poisoned_coffee"]
                if target in coffee_types:
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
                        self.O.remove_holding(target, where_coffee_at)
                    return True
                
                # replace cabinet for the secret room
                elif target == "cabinet":
                    if do_print:
                        print("You punched the cabinet", end="")
                        dotdotdot()
                        print("and broke your fingers! ouch!")
                        delay()
                        print("But as the cabinet breaks into pieces you see something suspicious behind it")
                    self.O.add_holding("broken_cabinet", "boss_office")
                    self.O.remove_holding("cabinet", "boss_office")
                    return True
                
                # add more items that can be destroyed later but right now only coffee and cabinet
                else:
                    if do_print:
                        print("uhh", end="")
                        dotdotdot()
                        print("no thank you")
                        delay()
                return False
            
            # cannot hit an item not in the room or inventory
            else:
                if do_print: print("You can't see that")
                return False
        
        if obj_type == "character":
            victim_name = self.O.get_character_data("name", target)
            inventory = self.O.get_holding(target)
            dropped_item = rnd.choice(inventory) if len(inventory) != 0 else None
            current_friendliness = self.O.get_character_data("friendliness", target)

            if target in self.O.get_holding(room):
                if target == character:
                    if not self.O.get_character_data("uses_parser", character):
                        # NPC will not punch itself
                        return False
                    if do_print:
                        print("Ughh, I hate myself!")
                        print("What is wrong with me!")
                        print(f"You {verb} yourself")
                        print(
                            f"You stumbled on the floor {f"and dropped {dropped_item}" if dropped_item is not None else ""}"
                        )
                if self.O.get_character_data("uses_parser", target):
                    # prints out since its relevant to the player
                    print(f"You {verb} {victim_name}", end="")
                    dotdotdot()
                    print(f"{f"{dropped_item} was dropped and " if dropped_item is not None else ""}{victim_name} falls on the floor")
                    delay()
                    print(f"{victim_name}: Whats the matter with you?")
                    delay()
                else:
                    if do_print:
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
                    self.O.change_holder(dropped_item, target, room)
                    if (
                        self.O.get_character_data("uses_parser", character)
                        and target != character
                    ):
                        self.O.set_character_data(
                            target, "friendliness", current_friendliness - 1
                        )

                return True
            
            else:
                if do_print:
                    print(f"{victim_name} isn't even there dummy")
                return False

        if obj_type == "static_character" and target in self.O.get_holding(room):
            victim_name = self.O.get_character_data("name", target)
            if target == "boss":
                current_likability = self.O.get_character_data("likability", character)
                if do_print:
                    print(f"{victim_name}: Rebelling against me eh?")
                    print("likability with boss decreased")
                self.O.set_character_data(character, "likability", current_likability - 3)
                return True
            else:
                if do_print:
                    print(f"Im scared to {verb} {victim_name}, they might report me")
                return False

        return False
    
    def thrown_obj_at_x(self, thrown_obj:objUID, target:objUID, character:objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        current_likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)

        # map to synonmys to use plus verify
        mapped_obj = self.map_to_actual_obj(thrown_obj, character)
        if mapped_obj == "no obj found":
            if do_print: print(f"{thrown_obj} is not in the game dictionary")
            return False
        else: thrown_obj = mapped_obj
        mapped_obj = self.map_to_actual_obj(target, character)
        if mapped_obj == "no obj found":
            if do_print: print(f"{target} is not in the game dictionary")
            return False
        else: target = mapped_obj
        obj_type = self.O.get_obj_type(thrown_obj)
        target_type = self.O.get_obj_type(target)
        
        # valid objects to throw and person to throw to
        if obj_type != "item":
            if do_print:
                print(f"How would you even throw that", end="")
                symsymsym("?")
            return False
        if target_type not in ["character", "static_character"]:
            if do_print: 
                print("What even would be the point of that")
            return False
        victim_name = self.O.get_character_data("name", target)
        
        if thrown_obj not in inventory:
            if do_print: print("Maybe try finding the item first, that would be smart.")
            return False
        if target not in self.O.get_holding(room):
            if do_print: print(f"Maybe try finding {victim_name} first, that would be smart")
            return False
        if target_type == "character":
            if target == character:
                if do_print:
                    print("How would I even throw something at myself?")
                return False
            if self.O.get_character_data("uses_parser", target):
                # prints out since its relevant to the player
                print(f"You threw {thrown_obj} at {victim_name}...")
                if thrown_obj == "coffee":
                    print(f"{victim_name}: I can't believe you threw coffee at me", end="")
                    symsymsym("!")
                    print("ugh, now I have to change my clothes!")
                    delay()
                    print(f"{victim_name} loses a turn")
                    delay()
                    self.O.set_character_data(target, "skip_turn", 1)
                    self.O.set_character_data(target, "skip_cause", f"coffee all over you")
                else:
                    print(f"{victim_name}: ouch! please don't do that again.")
            else:
                if do_print:
                    print(f"{victim_name} Ouch! why did you that!!")
                    print(f"Friendliness with {victim_name} decreased")
                current_friendliness = self.O.get_character_data("friendliness", target)
                self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        if target_type == "static_character":
            if target == "boss":
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
                current_friendliness = self.O.get_character_data("friendliness", target)
                self.O.set_character_data(character, "friendliness", current_friendliness - 1)
        self.O.change_holder(thrown_obj, character, room)
        return True

    def hack_computer(self, destination: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        inventory = self.O.get_holding(character)
        valid_destination = ["workstation_1", "workstation_2", "workstation_3", "player", "NPC_1", "NPC_2"]
        LIKABILITY_CUT = 8

        nameS = []
        for obj in valid_destination:
            if "name" in self.O[obj]:
                nameS.append(self.O[obj]["name"])
        valid_destination += nameS

        # map character names to use plus verify
        destination = self.map_to_actual_obj(destination, character)
        if destination == "no obj found":
            # it will be caught later in the code as an invalid destination
            pass

        if destination in valid_destination and "usb_hacking_script" in inventory and room == "offices":
            if do_print:
                print("You insert the USB hacking script into the computer.")
                delay()
                print("The computer starts running the script...")
                delay(3)
            if destination in ["workstation_1", "player"]:
                if do_print: 
                    print("Access granted! You successfully hacked workstation 1.")
                    print(f"{self.O.get_character_data("name", "player")} lost {LIKABILITY_CUT} likability for")
                player_likability = self.O.get_character_data("likability", "player")
                self.O.set_character_data("player", "likability", player_likability - LIKABILITY_CUT)
            elif destination in ["workstation_2", "NPC_1"]:
                if do_print: 
                    print("Access granted! You successfully hacked workstation 2.")
                    print(f"{self.O.get_character_data("name", "NPC_1")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as his background.")
                philip_likability = self.O.get_character_data("likability", "NPC_1")
                self.O.set_character_data("NPC_1", "likability", philip_likability - LIKABILITY_CUT)
            elif destination in ["workstation_3", "NPC_2"]:
                if do_print: 
                    print("Access granted! You successfully hacked workstation 3.")
                    print(f"{self.O.get_character_data("name", "NPC_2")} lost {LIKABILITY_CUT} likability for a picture of the Boss in a speedo as her background.")
                serah_likability = self.O.get_character_data("likability", "NPC_2")
                self.O.set_character_data("NPC_2", "likability", serah_likability - LIKABILITY_CUT)
            return True
        else:
            if destination not in valid_destination:
                if do_print: print(f"Not a valid target.")
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
    
    def give_coffee_or_poison(self, obj: objUID, taker: objUID, giver: objUID, do_print=True) -> bool:
        room = self.O.get_holder(giver)
        inventory = self.O.get_holding(giver)
        
        taker = self.map_to_actual_obj(taker, giver)

        if self.O.get_obj_type(taker) not in ["character", "static_character"]:
            if do_print:
                print(f"Giving to a {taker}, are you mad?")
            return False
        gifted_name = self.O.get_character_data("name", taker)
        current_friendliness = self.O.get_character_data("friendliness", taker)
        if obj == "coffee" and "poisoned_coffee" in inventory:  # + room_holdings
            obj = "poisoned_coffee"
        if obj in inventory:
            if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
                if do_print:
                    print("You cannot see anyone in this darkdness")
                    delay()
                    print("but im sure they'd like a warm coffee to wait it out")
                return False
            if taker in self.O.get_holding(room):
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
                    if self.O.get_character_data("uses_parser", giver):
                        self.O.set_character_data(
                            taker, "friendliness", current_friendliness - 2
                        )
                else:
                    if taker == "boss":
                        current_likability = self.O.get_character_data("likability", giver)
                        if do_print:
                            print("coffee is not a gift, it is a bribe", end="")
                            dotdotdot()
                            print("I like it.")
                            delay()
                            print("Your likability with the boss increased")
                        self.O.set_character_data(giver, "likability", current_likability + 4)
                    else:
                        if do_print:
                            print(f"{gifted_name}: Thanks for the coffee!")
                            delay()
                    if do_print:
                        print(f"Friendliness with {gifted_name} increased")
                    if self.O.get_character_data("uses_parser", giver):
                        self.O.set_character_data(
                            taker, "friendliness", current_friendliness + 3
                        )
                self.O.change_holder(obj, giver, taker)
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
    
    