from basic_actions import BasicActions
from sabotage_action import SabotageAction
from consume_actions import ConsumeAction
from work_actions import WorkActions
from events import Events

from obj_dict import ObjDict

type objUID = str

class Actions(BasicActions, SabotageAction, ConsumeAction, WorkActions, Events):

    # add the [] syntax notation like dictionary
    # e.g. Class["variables"] works as Class.variables
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def load_object_dictionary(self, obj_dict: ObjDict) -> None:
        self.O = obj_dict

    def load_events_data_structure(self, dict):
        for k, v in dict.items():
            self[k] = v


    def map_to_actual_obj(self, obj_synonym: objUID, character: objUID) -> objUID:

        # maps to actual object if given (well the object itself or ) the objects "name"
        for obj, attrS in self.O.items():
            if obj == obj_synonym:
                return obj
            if "name" in attrS and self.O.get_character_data("name", obj) == obj_synonym:
                return obj

        # the second argument is just used to identify the room and self
        # e.g. passing "room" maps to actual room
        room = self.O.get_holder(character)  

        # map local var value if it is same name as obj_name e.g. "myself" gets the key "character" which then maps to the character value and is returned
        mapped_obj = ""
        for obj, synonym_list in self.O["other_valid_obj_name"].items():
            for synonym in synonym_list:
                if obj_synonym == synonym:
                    mapped_obj = obj
                    break
            else:
                continue
            break
        for name, value in locals().items():
            if mapped_obj == name:
                return value

        # last check if mapped obj is valid
        if self.O.is_valid_obj(mapped_obj):
            return mapped_obj
        return "no obj found"