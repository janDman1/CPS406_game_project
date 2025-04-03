from utils import delay, dotdotdot

type objUID = str

class ConsumeAction:

    def consume_cake(self, obj: objUID, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)

        # process synonym, in this case "cake" to map to any in your inventory
        if obj == "cake":
            for item in inventory:
                if item in ["strawberry_cake", "chocolate_cake", "vanilla_cake"]:
                    obj = item

        # map the rest of synonyms
        obj = self.map_to_actual_obj(obj, character)

        if obj in inventory:
            if do_print: 
                print("You lavishly ate the whole cake")
                delay()
                print("mouth was filled with icing")
                delay()
                print("Your eyes dilated...")
                delay()
                print("You can feel the sugar enter your")
                delay()
                print("blood stream")
                delay()
                print("You are now on sugar-rush")
            # always with extra turn
            current_turn_speed = self.O.get_character_data("turn_speed", character)
            self.O.set_character_data(character, "turn_speed", current_turn_speed + 100)
            return True
        if do_print: print("You do not have cake with you")
        return False

    def consume_coffee(self, obj: objUID, character: objUID, do_print=True) -> bool:
        inventory = self.O.get_holding(character)
        if obj == "coffee" and "poisoned_coffee" in inventory:  # + room_holdings
            obj = "poisoned_coffee"
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("You sipped coffee in the middle of darkness")
                dotdotdot(False)
                print("while hearing your colleages fumble")
                delay()
                print("trying to find a flashlight")
                delay()
        if obj in inventory:
            if obj == "poisoned_coffee":
                self.consume_poison(obj, character, do_print)
            else:
                if do_print:
                    print(
                        "You felt a boost of energy!\n"
                        "It feels like you can do much more.\n"
                        'You are now "caffinated"!!'
                    )
                self.O.remove_holding(obj, character)
                self.O.set_character_data(character, "turn_speed", 120)
            return True
        return False

    def consume_poison(self, obj: objUID, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if obj in self.O.get_holding(character):
            if do_print:
                print(
                    "Ugh! You felt as if your stomach is about to explode\n"
                    "You hurried to the washroom..\n"
                    'You were "poisoned"!!'
                )
            self.O.remove_holding(obj, character)
            self.O.change_holder(character, room, "washroom")
            self.O.set_character_data(character, "turn_speed", 70)
            self.O.set_character_data(character, "skip_turn", 2)
            self.O.set_character_data(character, "skip_cause", f"you consumed {obj}")
            return True
        return False

    def consume_inedible(self, obj: str, character: str, do_print=True) -> bool:
        likability = self.O.get_character_data("likability", character)
        room = self.O.get_holder(character)
        inventory = self.O.get_holding(character)
        if self["variables"]["is_lights_out"] and "flashlight" not in inventory:
            if do_print:
                print("Don't even try because you cannot see anything")
            return False
        if obj in self.O.get_holding(character) + self.O.get_holding(room):
            if obj == "laxative":
                if do_print:
                    print("I am not drinking that")
                return False
            else:
                if do_print:
                    print(f"You tried to eat {obj}")
                    delay()
                    print(f"your teeth clangs to the sound of you biting the {obj}")
                    delay()
                    print(f"Someone spotted you accross the room!")
                    delay()
                    print("Your likability decreases")
                self.O.set_character_data(character, "likability", likability - 2)
                return True
        return False