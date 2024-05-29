import outlines
from typing import List

from texty.game import GameState, InternalState

@outlines.prompt
def rules():
    """
    ## Rules for the text adventure emulator:

    The model emulates an old school text adventure game. Text only. User navigates between different spaces or rooms, inspecting elements and taking actions. They have an inventory and can use their inventory within their actions.
    
    The model plans one step ahead. That is, it keeps track of all of the connected rooms and available actions
    within an area.
    """


@outlines.prompt
def game_ideas(suggestion: str):
    """
    List 5 game ideas based on the following concept: {suggestion}.

    Respond as a json array of strings
    """

@outlines.prompt
def gen_game_state(description: str):
    """
    Generate a scenario based on the following description: {description}

    A scenario consists of:
    - a starting room
    - a list of objectives. Once these are acheived, new objectives are created
    - a list of connected rooms, and where they are located relative the to the current room
    - a list of items within the room
    - a list of actions that can be taken

    Respond according to the schema:
    """