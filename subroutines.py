from basic_actions import BasicActions
from sabotage_action import SabotageActions
from consume_actions import ConsumeActions
from work_actions import WorkActions
from events import Events

class Subroutines(WorkActions, BasicActions, SabotageActions, ConsumeActions, Events):
    """Class to modify the data structure"""

    # looks empty but really combines all the actions and events into one class