import json
import unittest

from obj_dict import ObjDict
from parser import Parser
from utils import remove_comments


class TestParser(unittest.TestCase):
    def setUp(self):
        # Open and read the data.txt file safely using a with statement
        with open("data.txt", "r") as file:
            parsed_data_file = remove_comments(file.read())

        # Parse the JSON data
        data = json.loads(parsed_data_file)
        self.mock_parser = Parser(data["Commands"])

        # Create a mock ObjDict instance with mock data
        self.mock_obj_dict = ObjDict(
            {
                "item1": {
                    "type": "item",
                    "name": "sword",
                    "description": "A sharp blade",
                },
                "item2": {
                    "type": "item",
                    "name": "shield",
                    "description": "A sturdy shield",
                },
                "room1": {"type": "room", "description": "A dark room"},
                "other_valid_obj_name": {
                    "item1": ["blade", "weapon"],
                    "item2": ["armor", "protection"],
                    "networking_teamlead": ["Steve", "Jobs"],
                    "usb_hacking_script": ["usb", "script"],
                    "room": ["room", "around"],
                    "character": ["self", "yourself", "myself"],
                    "inventory": ["inventory"],
                },
            }
        )

        # self.parser = Parser()
        self.mock_parser.load_game_dictionary(self.mock_obj_dict)

    def test_fix_json_import(self):
        # Call the method to fix JSON import
        self.mock_parser.fix_json_import()

        # Check that verbs are converted to sets
        self.assertIsInstance(self.mock_parser["verbs"]["0"], set)
        self.assertIsInstance(self.mock_parser["verbs"]["1"], set)
        self.assertEqual(self.mock_parser["verbs"]["0"], {"N", "north", "NORTH"})
        self.assertEqual(self.mock_parser["verbs"]["1"], {"S", "south", "SOUTH"})

        # Check that articles are converted to a set
        self.assertIsInstance(self.mock_parser["articles"], set)
        self.assertEqual(self.mock_parser["articles"], {"of", "a", "an", "the"})

        # Check that prepositions are converted to a set
        self.assertIsInstance(self.mock_parser["prepositions"], set)
        self.assertEqual(self.mock_parser["prepositions"], {"and", "on", "to", "with"})

    def test_load_game_dictionary(self):
        # Call the method to load the game dictionary
        self.mock_parser.load_game_dictionary(self.mock_obj_dict)

        # Check that the game dictionary contains all valid object names
        expected_game_dictionary = {
            "usb",
            "script",
            "shield",
            "armor",
            "around",
            "yourself",
            "blade",
            "sword",
            "weapon",
            "protection",
            "Jobs",
            "self",
            "room",
            "myself",
            "inventory",
            "Steve",
        }
        self.assertEqual(self.mock_parser.game_dictionary, expected_game_dictionary)

    def test_parse_input_valid(self):
        # Test valid inputs
        result = self.mock_parser.parse_input("grab shield")
        self.assertEqual(result, [4, "shield", None, None])

        result = self.mock_parser.parse_input("look around")
        self.assertEqual(result, [12, "around", None, None])

    def test_parse_input_with_articles(self):
        # Test input with articles
        result = self.mock_parser.parse_input("grab a shield")
        self.assertEqual(result, [4, "shield", None, None])

    def test_parse_input_invalid(self):
        # Test invalid inputs
        result = self.mock_parser.parse_input("fly to the moon")
        self.assertEqual(result, [None, None, None, None])

    def test_find_subroutine_call_exact_match(self):
        # Test exact matches in the lookup table
        result = self.mock_parser.find_subroutine_call(
            [21, "laxative", "and", "coffee", "make_poisoned_coffee"],
        )
        self.assertEqual(result, "make_poisoned_coffee")

    def test_find_subroutine_call_with_wildcards(self):
        # Test matches with wildcards in the lookup table
        result = self.mock_parser.find_subroutine_call([13, "coffee", "to", "player"])
        self.assertEqual(result, "give_coffee_or_poison")

    def test_find_subroutine_call_no_match(self):
        # Test when no match is found
        result = self.mock_parser.find_subroutine_call([4, "unknown", "with", "object"])
        self.assertEqual(result, "no match")

    def test_get_back_the_verb_string(self):
        # Test finding the verb string in the unprocessed command
        result = self.mock_parser.get_back_the_verb_string(4, "grab the coffee")
        self.assertEqual(result, "grab")

        # Test when the verb is not found
        result = self.mock_parser.get_back_the_verb_string(0, "fly to the moon")
        self.assertEqual(result, "no verb found")

    def test_get_random_verb_string(self):
        # Test that the result is always one of the verbs in the mock data
        result = self.mock_parser.get_random_verb_string(0)
        self.assertIn(result, ["N", "north", "NORTH"])


if __name__ == "__main__":
    unittest.main()
