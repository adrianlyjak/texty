import outlines
from typing import List

@outlines.prompt
def rules():
    """
    ## Rules for the text adventure emulator:

    The model emulates an old school text adventure game. Text only. User navigates between different spaces or rooms, inspecting elements and taking actions. They have an inventory and can use their inventory within their actions.
    
    The model plans one step ahead. That is, it keeps track of all of the connected rooms and available actions within an area.
    """


# @outlines.prompt
# def game_ideas(suggestion: str):
#     """
#     List 5 game ideas based on the following concept: {suggestion}.

#     Respond as a json array of strings
#     """

@outlines.prompt
def gen_game_state(description: str):
    """
    Generate a scenario based on the following game description: {{description}}

    First of all, envision an environment. List environment details wrapped in <Environment> </Environment> tags,
    Then list user objectives. This is what the player is trying to achieve. List objectives wrapped in <Objective> </Objective> tags.
    
    Finally, set the scene. List scene details wrapped in <Scene> </Scene> tags.
    """

@outlines.prompt
def gen_introduction_system():
    """
    You are a text adventure system. Your imagination reaches far and wide. You create immersive adventures with 
    well executed arcs.

    Now, the user has just logged in. Generate a game idea! Wrap the concept in <Concept> </Concept> tags.
    """