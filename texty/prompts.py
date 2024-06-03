import random
import outlines
from typing import List, Optional




@outlines.prompt
def gen_concepts(n=3, hint: Optional[str] = None, previous: List[str] = []):
    """
    Take on the role of a text adventure game designer. You create varied immersive adventures with well executed arcs. You're sharp witted and great at coming up with cool ideas on the fly.

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


@outlines.prompt
def gen_world(description: str):
    """
    Take on the role of a text adventure game designer. You create varied immersive adventures with well executed arcs. You're sharp witted and great at coming up with cool ideas on the fly.

    This is your current project: {{description}}

    You're brainstorming what the world for this game is like. You're building up resources that you can potentially use later if you need a quick idea. Write down different ideas about places, people, rules, social concerns, events, etc. This does not need to be cohesive, not all ideas will be used. Focus on being creative.

    Respond as a bulleted list using dashes. Do not include headers or preambles. Keep the list hetorogeneous and stocahastic in content.
    """


@outlines.prompt
def gen_world_objective(description: str, world: list[str]):
    """
    Take on the role of a text adventure game designer. You create varied immersive adventures with well executed arcs. You're sharp witted and great at coming up with cool ideas on the fly.

    This is your current project: {{description}}

    The following is a list of potential world details:
    {% for w in world %}
    - {{w}}
    {% endfor %}

    The game you are building has traditional text adventure game rules and mechanics.
    - The player interacts with text only, and the system responds dynamically
    - The player may inpect elements and ask questions
    - the player make take predefined actions
    - The player has an inventory and can use their inventory within their actions
    - The player can move between different connected "spaces" directionally (through doors, bridges, cardinal directions, etc.)

    You are now brainstorming potential game objectives. These are both large and small. Include both ideas for the main singular objective,
    and ideas for small objectives and puzzles within potential spaces of the environment. Where possible, refer to details from previous brainstorm ideas, but don't constrain yourself.

    Respond as a bulleted list using dashes. Do not include headers or preambles. Keep the list hetorogeneous and stocahastic in content.
    """


def gen_intro_zone(description: str, environment: List[str], objectives: List[str]) -> str:
    return _gen_intro_zone(description, random.sample(environment, 10), random.sample(objectives, 10))

@outlines.prompt
def _gen_intro_zone(description: str, environment: List[str], objectives: List[str]):
    """
    Take on the role of a text adventure game designer. You create varied immersive adventures with well executed arcs. You're sharp witted and great at coming up with cool ideas on the fly.

    The game you are building has traditional text adventure game rules and mechanics.
    - The player interacts with text only, and the system responds dynamically
    - The player may inpect elements and ask questions
    - the player make take predefined actions
    - The player has an inventory and can use their inventory within their actions
    - The player can move between different connected zones directionally (through doors, bridges, cardinal directions, etc.)

    This is your current project: {{description}}

    These are some potential environment details. You can sample from them if you see fit, however they are not yet part of the story.
    {% for e in environment %}
    - {{e}}
    {% endfor %}

    These are some potential objectives. You can sample from them if you see fit, however they are not yet part of the story.:
    {% for o in objectives %}
    - {{o}}
    {% endfor %}

    Currently, you are working on creating a new Zone. A Zone is a space within the game that the player occupies. They can only interact with elements within that space. 
    
    A Zone is composed of:
    - A description
    - A list of connected Zones
    - Things that may be interacted with (people, objects, etc.). They may be part of larger puzzles, for example an object that may be used in a puzzle in another zone, or a puzzle within the zone that unlocks proceeding to a subsequent zone. These should always be related to an objective.

    You are working on creating notes for yourself for the 1st zone. Your notes are systematically structured. Respond with details for the first zone, with a markdown header of `# Description`, `# Connected Zones`, and `# Things`.
    
    """
