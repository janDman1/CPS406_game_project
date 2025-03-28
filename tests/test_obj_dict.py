import unittest
from obj_dict import ObjDict


class TestObjDict(unittest.TestCase):
    def setUp(self):
        # Create mock data for testing
        self.mock_obj_dict = ObjDict(
            {
                "item1": {
                    "type": "item",
                    "description": "A test item",
                    "holder": "room1",
                    "attributes": ["fragile", "valuable"],
                },
                "item2": {
                    "type": "item",
                    "description": "Another test item",
                    "holder": "room1",
                    "attributes": [],
                },
                "item3": {
                    "type": "item",
                    "description": "Another test item",
                    "holder": None,
                    "attributes": ["flammable"],
                },
                "room1": {
                    "type": "room",
                    "description": "A test room",
                    "holder": None,
                    "NSEW": ["room2", None, "room3", None],
                },
                "room2": {
                    "type": "room",
                    "description": "Another test room",
                    "holder": None,
                    "NSEW": [None, "room1", None, None],
                },
                "room3": {
                    "type": "room",
                    "description": "A third test room",
                    "holder": None,
                    "NSEW": [None, None, None, "room1"],
                },
                "invalid_obj": "This is not a valid object",
                "character1": {
                    "type": "character",
                    "name": "John",
                    "status": ["healthy"],
                    "likability": 5,
                    "dialogue": ["Hello!", "How are you?"],
                    "friendliness": 3,
                    "turn_speed": 100,
                    "skip_turn": 0,
                    "skip_cause": None,
                    "uses_parser": True,
                },
                "character2": {
                    "type": "character",
                    "name": "Jane",
                    "status": ["poisoned"],
                    "likability": -2,
                    "dialogue": ["Go away!", "Leave me alone!"],
                    "friendliness": 0,
                    "turn_speed": 80,
                    "skip_turn": 1,
                    "skip_cause": "poison",
                    "uses_parser": False,
                },
            }
        )

    def test_get_obj_type_valid(self):
        # Test with a valid object
        self.assertEqual(self.mock_obj_dict.get_obj_type("item1"), "item")
        self.assertEqual(self.mock_obj_dict.get_obj_type("room1"), "room")

    def test_get_obj_type_invalid(self):
        # Test with an invalid object
        self.assertEqual(
            self.mock_obj_dict.get_obj_type("nonexistent"), "invalid object"
        )
        self.assertEqual(
            self.mock_obj_dict.get_obj_type("invalid_obj"), "invalid object"
        )

    def test_is_valid_obj(self):
        # Test valid objects
        self.assertTrue(self.mock_obj_dict.is_valid_obj("item1"))
        self.assertTrue(self.mock_obj_dict.is_valid_obj("room1"))

        # Test invalid objects
        self.assertFalse(self.mock_obj_dict.is_valid_obj("nonexistent"))
        self.assertFalse(self.mock_obj_dict.is_valid_obj("invalid_obj"))

    def test_get_obj_description(self):
        # Test valid objects
        self.assertEqual(self.mock_obj_dict.get_obj_description("item1"), "A test item")
        self.assertEqual(self.mock_obj_dict.get_obj_description("room1"), "A test room")

        # Test invalid object (should raise KeyError)
        with self.assertRaises(KeyError):
            self.mock_obj_dict.get_obj_description("nonexistent")

    def test_initiate_holdings(self):
        # Call the method to initialize holdings
        self.mock_obj_dict.initiate_holdings()

        # Check that the "holding" attribute is correctly populated
        self.assertIn("holding", self.mock_obj_dict["room1"])
        self.assertIn("item1", self.mock_obj_dict["room1"]["holding"])
        self.assertIn("item2", self.mock_obj_dict["room1"]["holding"])

        # Check that rooms with no items have an empty "holding" list
        self.assertIn("holding", self.mock_obj_dict["room2"])
        self.assertEqual(self.mock_obj_dict["room2"]["holding"], [])

    def test_get_holder(self):
        # Test getting the holder of valid items
        self.assertEqual(self.mock_obj_dict.get_holder("item1"), "room1")
        self.assertEqual(self.mock_obj_dict.get_holder("item2"), "room1")

        # Test getting the holder of a room (should be None)
        self.assertIsNone(self.mock_obj_dict.get_holder("room1"))

    def test_get_holding(self):
        # Call initiate_holdings to populate the "holding" attribute
        self.mock_obj_dict.initiate_holdings()

        # Test getting the holding list of a room with items
        self.assertEqual(
            set(self.mock_obj_dict.get_holding("room1")), {"item1", "item2"}
        )

        # Test getting the holding list of a room with no items
        self.assertEqual(self.mock_obj_dict.get_holding("room2"), [])

    def test_add_holding(self):
        # Add a new item to room1
        self.mock_obj_dict.add_holding("item3", "room1")
        self.assertIn("item3", self.mock_obj_dict["room1"]["holding"])

        # Add an empty holding list to room2
        self.mock_obj_dict.add_holding(None, "room2")
        self.assertEqual(self.mock_obj_dict["room2"]["holding"], [])

    def test_remove_holding(self):
        # Call initiate_holdings to populate the "holding" attribute
        self.mock_obj_dict.initiate_holdings()

        # Remove an item from room1
        self.mock_obj_dict.remove_holding("item1", "room1")
        self.assertNotIn("item1", self.mock_obj_dict["room1"]["holding"])

    def test_remove_holder(self):
        # Remove the holder of an item
        self.mock_obj_dict.remove_holder("item1")
        self.assertIsNone(self.mock_obj_dict["item1"]["holder"])

    def test_remove_holder(self):
        # Test removing the holder of an item
        self.mock_obj_dict.remove_holder("item1")
        self.assertIsNone(self.mock_obj_dict["item1"]["holder"])

        # Ensure it doesn't affect other items
        self.assertEqual(self.mock_obj_dict["item2"]["holder"], "room1")

    def test_change_holder(self):
        # Call initiate_holdings to populate the "holding" attribute
        self.mock_obj_dict.initiate_holdings()

        # Test changing the holder of an item
        self.mock_obj_dict.change_holder("item1", "room1", "room2")

        # Verify that the item is removed from the old holder
        self.assertNotIn("item1", self.mock_obj_dict["room1"]["holding"])

        # Verify that the item is added to the new holder
        self.assertIn("item1", self.mock_obj_dict["room2"]["holding"])

        # Verify that the item's holder is updated
        self.assertEqual(self.mock_obj_dict["item1"]["holder"], "room2")

    def test_find_next_room(self):
        # Test valid directions
        self.assertEqual(self.mock_obj_dict.find_next_room("N", "room1"), "room2")
        self.assertEqual(self.mock_obj_dict.find_next_room("E", "room1"), "room3")
        self.assertEqual(self.mock_obj_dict.find_next_room("S", "room2"), "room1")
        self.assertEqual(self.mock_obj_dict.find_next_room("W", "room3"), "room1")

        # Test invalid directions (should return None)
        self.assertIsNone(self.mock_obj_dict.find_next_room("S", "room1"))
        self.assertIsNone(self.mock_obj_dict.find_next_room("W", "room1"))
        self.assertIsNone(self.mock_obj_dict.find_next_room("N", "room3"))

    def test_has_item_attribute(self):
        # Test items with attributes
        self.assertTrue(self.mock_obj_dict.has_item_attribute("fragile", "item1"))
        self.assertTrue(self.mock_obj_dict.has_item_attribute("valuable", "item1"))

        # Test items without the specified attribute
        self.assertFalse(self.mock_obj_dict.has_item_attribute("fragile", "item2"))
        self.assertFalse(self.mock_obj_dict.has_item_attribute("valuable", "item2"))

        # Test invalid item (should raise KeyError)
        with self.assertRaises(KeyError):
            self.mock_obj_dict.has_item_attribute("fragile", "nonexistent_item")

    def test_get_character_data_valid(self):
        # Test retrieving valid character data
        self.assertEqual(
            self.mock_obj_dict.get_character_data("name", "character1"), "John"
        )
        self.assertEqual(
            self.mock_obj_dict.get_character_data("status", "character1"), ["healthy"]
        )
        self.assertEqual(
            self.mock_obj_dict.get_character_data("likability", "character2"), -2
        )
        self.assertEqual(
            self.mock_obj_dict.get_character_data("dialogue", "character2"),
            ["Go away!", "Leave me alone!"],
        )

    def test_get_character_data_invalid(self):
        # Test retrieving invalid character data (should raise KeyError)
        with self.assertRaises(KeyError):
            self.mock_obj_dict.get_character_data("invalid_data", "character1")

        with self.assertRaises(KeyError):
            self.mock_obj_dict.get_character_data("name", "nonexistent_character")

    def test_set_character_data_valid(self):
        # Test setting valid character data
        self.mock_obj_dict.set_character_data("character1", "likability", 10)
        self.assertEqual(self.mock_obj_dict["character1"]["likability"], 10)

        self.mock_obj_dict.set_character_data("character2", "status", ["healthy"])
        self.assertEqual(self.mock_obj_dict["character2"]["status"], ["healthy"])

    def test_set_character_data_invalid(self):
        # Test setting invalid character data (should raise KeyError)
        with self.assertRaises(KeyError):
            self.mock_obj_dict.set_character_data("character1", "invalid_data", "value")

        with self.assertRaises(KeyError):
            self.mock_obj_dict.set_character_data(
                "nonexistent_character", "name", "New Name"
            )


if __name__ == "__main__":
    unittest.main()
