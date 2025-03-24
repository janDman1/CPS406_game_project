from jan_game_base import Events

# This is your entire domain, feel free to do *anything* you'd like

type objUID = str  # just means objUID is type string

class Events_Expanded(Events):
    def email_function(self, arg:str, character:objUID, do_print=True) -> None:
        pass

    # here try to override inventory
    def show_inventory(self, character:objUID, do_print=True) -> bool:
        pass