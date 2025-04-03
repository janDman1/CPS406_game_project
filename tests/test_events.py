import unittest
from unittest.mock import MagicMock, patch
from all_actions import Actions as Events


class TestEvents(unittest.TestCase):
    def setUp(self):
        self.events = Events()
        self.events.O = MagicMock()
        self.events.map_to_actual_obj = MagicMock()
        self.events["variables"] = {
            "is_boss_anniversary": False,
            "is_lights_out": False,
            "MAX_INVENTORY": 5,
        }
        self.events.delay = MagicMock()
        self.events.dotdotdot = MagicMock()

    def test_set_get_item(self):
        self.events["email_gen"] = "test@example.com"
        self.assertEqual(self.events["email_gen"], "test@example.com")

    def test_load_object_dictionary(self):
        mock_obj_dict = MagicMock()
        self.events.load_object_dictionary(mock_obj_dict)
        self.assertEqual(self.events.O, mock_obj_dict)

    def test_go_direction_valid_move(self):
        character = "char1"
        self.events.O.is_valid_obj.return_value = True
        self.events.O.get_obj_type.return_value = "character"
        self.events.O.get_holder.return_value = "room1"
        self.events.direction = MagicMock(return_value=["N"])
        self.events.O.find_next_room.return_value = "room2"
        self.events.O.get_holding.return_value = []
        self.events.O.change_holder = MagicMock()
        self.events.show_character_view = MagicMock()

        result = self.events.go_direction(0, character, do_print=False)

        self.assertTrue(result)
        self.events.O.change_holder.assert_called_with(character, "room1", "room2")
        self.events.show_character_view.assert_called_with(character, False, False)

    @patch("builtins.print")
    def test_show_character_view_no_print(self, mock_print):
        character = "char1"
        result = self.events.show_character_view(character, do_print=False)
        self.assertTrue(result)
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_show_character_view_lights_out_no_flashlight(self, mock_print):
        character = "char1"
        self.events.O.get_holder.return_value = "room1"
        self.events.O.get_holding.side_effect = lambda x: (
            [character] if x == "room1" else []
        )
        self.events["variables"]["is_lights_out"] = True

        with patch.object(self.events, "delay") as mock_delay:
            result = self.events.show_character_view(character, do_print=True)

        self.assertFalse(result)
        mock_print.assert_any_call("It's too dark, I cannot see anything")
        mock_print.assert_any_call("Maybe a flashlight will help")

    @patch("builtins.print")
    def test_show_character_view_valid_room(self, mock_print):
        character = "char1"
        self.events.O.get_holder.return_value = "room1"
        self.events.O.get_holding.side_effect = lambda x: (
            [character, "item1", "npc1"] if x == "room1" else []
        )
        self.events.O.get_obj_description.return_value = "A bright room"
        self.events.O.get_obj_type.side_effect = lambda x: (
            "character" if x == "npc1" else "object"
        )
        self.events.O.get_character_data.return_value = "NPC Name"
        self.events.direction = MagicMock(side_effect=lambda x: x)
        self.events.O.find_next_room.side_effect = lambda i, r: (
            "room2" if i in ["N", "E"] else None
        )
        self.events.print_list = MagicMock()

        result = self.events.show_character_view(character, do_print=True)

        self.assertTrue(result)
        mock_print.assert_any_call("ROOM1")
        self.events.print_list.assert_called_with(["item1", "NPC Name"])
        mock_print.assert_any_call("to the N is room2")
        mock_print.assert_any_call("to the E is room2")

    @patch("builtins.print")
    def test_drop_obj_success(self, mock_print):
        character = "char1"
        obj = "item1"
        self.events.O.get_holding.return_value = ["item1"]
        self.events.O.is_valid_obj.return_value = True
        self.events.O.get_holder.return_value = "room1"
        self.events.map_to_actual_obj.return_value = "item1"

        result = self.events.drop_obj(obj, character, do_print=True)

        self.assertTrue(result)
        self.events.O.change_holder.assert_called_with("item1", character, "room1")
        mock_print.assert_called_with("Done")

    @patch("builtins.print")
    def test_drop_obj_not_in_inventory(self, mock_print):
        character = "char1"
        obj = "item1"
        self.events.O.get_holding.return_value = []  # Character doesn't have the item
        self.events.map_to_actual_obj.return_value = "item1"

        result = self.events.drop_obj(obj, character, do_print=True)

        self.assertFalse(result)
        self.events.O.change_holder.assert_not_called()
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_drop_obj_invalid_object(self, mock_print):
        character = "char1"
        obj = "item1"
        self.events.O.get_holding.return_value = ["item1"]
        self.events.O.is_valid_obj.return_value = False  # Object is invalid
        self.events.map_to_actual_obj.return_value = "item1"

        result = self.events.drop_obj(obj, character, do_print=True)

        self.assertFalse(result)
        self.events.O.change_holder.assert_not_called()
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_drop_obj_maps_coffee_to_poisoned_coffee(self, mock_print):
        character = "char1"
        obj = "coffee"
        self.events.O.get_holding.return_value = ["poisoned_coffee", "coffee"]
        self.events.O.is_valid_obj.return_value = True
        self.events.O.get_holder.return_value = "room1"
        self.events.map_to_actual_obj.return_value = "poisoned_coffee"

        result = self.events.drop_obj(obj, character, do_print=True)

        self.assertTrue(result)
        self.events.O.change_holder.assert_called_with(
            "poisoned_coffee", character, "room1"
        )
        mock_print.assert_called_with("Done")

    @patch("builtins.print")
    def test_drop_obj_not_found_in_dictionary(self, mock_print):
        character = "char1"
        obj = "unknown_obj"
        self.events.map_to_actual_obj.return_value = "no obj found"

        result = self.events.drop_obj(obj, character, do_print=True)

        self.assertFalse(result)
        mock_print.assert_called_with("no obj found is not in the game dictionary")


if __name__ == "__main__":
    unittest.main()
