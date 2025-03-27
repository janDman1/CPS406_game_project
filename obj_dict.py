from pprint import pprint


type objUID = str


class ObjDict(dict):
    """
    Isolate game Data Structure and the Methods into this class.
    Also used for save and load feature.
    """

    # adds the dot (.) syntax notation for dictionary
    # e.g. Class.holder works as Class["holder"]
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def print_obj(self, obj: objUID) -> None:
        """For debugging :)"""
        if self.is_valid_obj(obj):
            obj_str = {obj: self[obj]}
            pprint(obj_str)

    def get_obj_type(self, obj: objUID) -> str:
        if self.is_valid_obj(obj):
            return self[obj]["type"]
        return "invalid object"

    def is_valid_obj(self, obj: objUID):
        if obj not in self:
            return False
        if not isinstance(self[obj], dict):
            return False
        for attr in ["type", "description", "holder"]:
            if attr not in self[obj].keys():
                return False
        return True

    def get_obj_description(self, obj: objUID) -> str:
        return self[obj]["description"]

    def initiate_holdings(self) -> None:
        """
        follow the object holder and add into holding,
        adding empty holding for the object
        (which might or might not be rewritten)
        while traversing all objects in ObjDict
        """
        visited = set()
        for obj in self.keys():
            if self.is_valid_obj(obj):
                src_obj = self[obj]["holder"]
                if src_obj is not None:
                    self.add_holding(obj, src_obj, False)
                    visited.add(src_obj)
                if obj not in visited:
                    self.add_holding(None, obj, False)

    def get_holder(self, obj: objUID) -> objUID:
        return self[obj]["holder"]

    def get_holding(self, obj: objUID) -> list[objUID]:
        return self[obj]["holding"].copy() if "holding" in self[obj] else []

    def add_holding(
        self, obj: None | objUID, src_obj: objUID, holder_update=True
    ) -> None:
        if self.is_valid_obj(src_obj):  # only works if source object exists/valid
            if obj is None:
                if "holding" not in self[src_obj]:
                    self[src_obj]["holding"] = []
            elif self.is_valid_obj(obj):
                if "holding" not in self[src_obj]:
                    self[src_obj]["holding"] = [obj]
                else:  # already has "holding"
                    self[src_obj]["holding"].append(obj)

                if holder_update:
                    self[obj]["holder"] = src_obj  # point obj to newest holder

    def remove_holding(self, obj: objUID, src_obj: objUID, holder_update=True) -> None:
        self[src_obj]["holding"].remove(obj)
        if holder_update:
            self.remove_holder(obj)

    def remove_holder(self, obj: objUID) -> None:
        self[obj]["holder"] = None

    def change_holder(self, obj: objUID, src_obj: objUID, dest_obj: objUID) -> None:
        self.remove_holding(obj, src_obj, False)
        self.add_holding(obj, dest_obj)

    type room_objUID = str

    def find_next_room(self, dir: str, room: room_objUID) -> room_objUID | None:
        if dir == "N":
            return self[room]["NSEW"][0]
        if dir == "S":
            return self[room]["NSEW"][1]
        if dir == "E":
            return self[room]["NSEW"][2]
        if dir == "W":
            return self[room]["NSEW"][3]
        return None

    def has_item_attribute(self, attr: str, obj: objUID) -> bool:
        return attr in self[obj]["attributes"]

    def get_character_data(self, data: str, char: objUID):  # -> str|int|None:
        if data not in [
            "name",
            "status",
            "likability",
            "dialogue",
            "friendliness",
            "turn_speed",
            "skip_turn",
            "skip_cause",
            "uses_parser",
        ]:
            raise KeyError(f"No {data} object Data in {char}")
        return self[char][data]

    def set_character_data(self, char: str, data: str, value: str | int | bool) -> None:
        if data not in [
            "name",
            "status",
            "likability",
            "dialogue",
            "friendliness",
            "turn_speed",
            "skip_turn",
            "skip_cause",
            "uses_parser",
        ]:
            raise KeyError(f"No {data} object Data in {char}")
        self[char][data] = value
