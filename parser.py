from obj_dict import ObjDict
import random as rnd
type subroutineID = str


class Parser(dict):
    """Parser for IO with user input and game output"""

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
        # adds the dot (.) syntax for dictionary
        # e.g. Class.holder works as Class["holder"]

    def fix_json_import(self) -> None:
        "fix data stuct lists into sets for better lookup"
        for k, l in self["verbs"].items():
            self["verbs"][k] = set(l)
        self["articles"] = set(self["articles"])
        self["prepositions"] = set(self["prepositions"])

    def load_game_dictionary(self, O: ObjDict) -> None:
        "makes a set of all the objects in game for object lookup"

        self.objects_dictionary = O.copy()
        obj_nameS = set()
        for k in O.keys():
            if O.is_valid_obj(k):
                obj_nameS.add(k)
            else:
                self.objects_dictionary.pop(k)
            if "name" in O[k]:
                nam = O[k]["name"]
                if nam != None:
                    obj_nameS.add(nam)

        valid_obj_synonyms = set()
        for _o, synonym_lst in O["other_valid_obj_name"].items():
            for s in synonym_lst:
                valid_obj_synonyms.add(s)

        self.game_dictionary = obj_nameS.union(valid_obj_synonyms)

    def parse_input(self, user_input: str) -> list[int | str | None]:
        """
        Parses user input into mapable [verb:int, obj1:str, prep:str, obj2:str] for lookup in lookup_table e.g. [put, laxative, in, coffee].
        Verifies if verbs, objects, and preposition are valid.
        """
        verb, obj1, prep, obj2 = None, None, None, None
        unprocessed_list = user_input.split()
        v_idx = None
        o1_idx = None
        p_idx = None
        o2_idx = None
        list_after_verb = []

        for a in self["articles"]:
            for _ in range(len(unprocessed_list)):
                try:
                    unprocessed_list.remove(a)
                except:
                    continue

        for v, synonymS in self["verbs"].items():
            for s in synonymS:
                try:
                    v_idx = unprocessed_list.index(s)
                    try:
                        list_after_verb = unprocessed_list[v_idx + 1 :]
                    except:
                        pass
                    verb = int(v)
                    break
                except ValueError:
                    continue
            if verb is not None:
                break

        # obj1 eaten
        for valid_obj in self["game_dictionary"]:
            try:
                o1_idx = list_after_verb.index(valid_obj)
                break
            except:
                continue

        # obj2 eaten
        for valid_obj in self["game_dictionary"]:
            try:
                next_obj_idx = list_after_verb.index(valid_obj)
                if next_obj_idx != o1_idx:
                    o2_idx = next_obj_idx
                    break
                continue
            except:
                continue

        if o2_idx is not None and o1_idx is not None:
            if o1_idx > o2_idx:
                o1_idx, o2_idx = o2_idx, o1_idx
        obj1 = list_after_verb[o1_idx] if o1_idx is not None else None
        obj2 = list_after_verb[o2_idx] if o2_idx is not None else None

        for i,w in enumerate(list_after_verb):
            if w in self["prepositions"]:
                p_idx = i
                prep = w
                break

        return (
            [verb, None, None, None] if o1_idx is None or obj1 is None 
            else [verb, obj1, None, None] if p_idx is None or 
                prep is None or (o1_idx < p_idx and obj2 is None)
            # obj1 will never be None before obj2 thus below
            else [verb, None, prep, obj1] if o1_idx > p_idx 
            else [verb, obj1, prep, obj2]
        )

    def find_subroutine_call(self, cmd: list[int | str | None]) -> subroutineID:
        """maps user input to subroutine_key (aka eventID), optimally using trie"""
        impossible_val = 10  # impossible because max score is 3
        score = [impossible_val] * len(self["lookup_table"])
        for i, match in enumerate(self["lookup_table"]):
            if cmd == match[:4]:
                return match[4]
            match_verb = cmd[0] == match[0]
            match_obj1 = cmd[1] == match[1] or match[1] == "*" and cmd[1] is not None
            match_preb = cmd[2] == match[2] or match[2] == "*" and cmd[2] is not None
            match_obj2 = cmd[3] == match[3] or match[3] == "*" and cmd[3] is not None
            if match_verb and match_obj1 and match_obj1 and match_preb and match_obj2:
                score[i] = 0
                if match[1] == "*":
                    score[i] += 1
                if match[2] == "*":
                    score[i] += 1
                if match[3] == "*":
                    score[i] += 1
        best_match = 0 if score[0] is not impossible_val else None
        min_so_far = score[0]
        for i, v in enumerate(score[0:]):
            if v is not impossible_val:
                if v < min_so_far:
                    min_so_far = v
                    best_match = i
        return (
            self["lookup_table"][best_match][4]
            if best_match is not None
            else "no match"
        )

    def get_back_the_verb_string(self, verb: int, unprocessed_cmd: str) -> str:
        for v in self["verbs"][str(verb)]:
            if v in unprocessed_cmd:
                return v
        return "no verb found"

    def get_random_verb_string(self, verb: int) -> str:
        return rnd.choice(list(self["verbs"][str(verb)]))

    def help_command(self, do_print) -> bool:
        if do_print:
            print("COMMANDS [WORDS] <OPTIONAL>")
            print("----------------------------")
            print(self["help"])

        # you can always use the help command without losing turns
        return False
