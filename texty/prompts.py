import outlines
from typing import List, Optional

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
def gen_world(description: str):
    """
    Generate a scenario based on the following game description: {{description}}

    First of all, envision an environment. List environment details wrapped in <Environment> </Environment> tags,
    Then list user objectives. This is what the player is trying to achieve. List objectives wrapped in <Objective> </Objective> tags.
    
    Finally, set the scene. List scene details wrapped in <Scene> </Scene> tags.
    """


@outlines.prompt
def gen_concepts(n=3, hint: Optional[str] = None, previous: List[str] = []):
    """
    Take on the role of a text adventure game designer. You create varied immersive adventures with 
    well executed arcs.

    What are some game concepts? Respond as a bulleted list using dashes.
    
    Example Response:

    - A mystery game set in a small town, where you must solve the murder of a local resident.
    - A survival game set in a post-apocalyptic world, where you must scavenge for food and supplies and avoid the zombies that roam the streets.
    - A puzzle game set in a labyrinth, where you must use your wits to find your way out.
    - A role-playing game set in a fantasy world, where you must choose your own adventure and make decisions that will affect the outcome of the story.
    {% for p in previous %}
    - {{p}}
    {% endfor %}

    What are {{n}} more game ideas? {% if hint %}Specifically, the player is interested in a game like this: '{{hint}}'{% endif %}
    """