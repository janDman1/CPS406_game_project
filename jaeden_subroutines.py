from jan_game_base import Events


type objUID = str  # just means objUID is type string

class Events_Expanded(Events):
    def __init__(self):
        super().__init__()
        self.email_gen = None  # Initialize the email generator

    def email_work(self, character: objUID, do_print=True) -> bool:
        room = self.O.get_holder(character)
        if room == "offices":
            print("Logging into computer to check emails/work.........\n")
            
            # Initialize the generator only once
            if self.email_gen is None:
                self.email_gen = self.email_generator()

            try:
                # Get the next email from the generator
                email_message, email_score = next(self.email_gen)
                print(email_message)
                print(f"Impact on reputation: {email_score}\n")
            except StopIteration:
                print("No more emails to read.")
                self.email_gen = None  # Reset the generator once all emails are read
            
            return True
        print("You need to go to the offices to do this")
        return False

    # Generator to yield one email at a time
    def email_generator(self):
        for email, score in self["email_minigame"].items():
            yield email, score

    # Here try to override inventory
    def show_inventory(self, character: objUID, do_print=True) -> bool:
        pass
