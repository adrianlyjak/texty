import dataclasses
import json
import random
import outlines
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


PROMPT_ROLE_GAME_DESIGNER = "Take on the role of a text adventure game designer. You create varied immersive adventures with well executed arcs. You're sharp witted and great at coming up with cool ideas on the fly."

PROMPT_MECHANICS = """The game you are building has traditional text adventure game rules and mechanics.
- The player interacts with text only, and the system responds dynamically
- The player may inpect elements and ask questions
- the player make take predefined actions
- The player has an inventory and can use their inventory within their actions
- The player can move between different connected "spaces" directionally (through doors, bridges, cardinal directions, etc.)"""


@outlines.prompt
def gen_concepts(
    n=3,
    hint: Optional[str] = None,
    previous: List[str] = [],
    role=PROMPT_ROLE_GAME_DESIGNER,
):
    """
    {{role}}

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
def gen_world(description: str, role=PROMPT_ROLE_GAME_DESIGNER):
    """
    {{role}}

    This is your current project: {{description}}

    You're brainstorming what the world for this game is like. You're building up resources that you can potentially use later if you need a quick idea. Write down different ideas about places, people, rules, social concerns, events, etc. This does not need to be cohesive, not all ideas will be used. Focus on being creative.

    Respond as a bulleted list using dashes. Do not include headers or preambles. Keep the list hetorogeneous and stocahastic in content.
    """


@outlines.prompt
def gen_world_objective(
    description: str,
    world: list[str],
    role=PROMPT_ROLE_GAME_DESIGNER,
    mechanics: str = PROMPT_MECHANICS,
):
    """
    {{role}}

    This is your current project: {{description}}

    The following is a list of potential world details:
    {% for w in world %}
    - {{w}}
    {% endfor %}

    {{mechanics}}

    You are now brainstorming potential game objectives. These are both large and small. Include both ideas for the main singular objective,
    and ideas for small objectives and puzzles within potential spaces of the environment. Where possible, refer to details from previous brainstorm ideas, but don't constrain yourself.

    Respond as a bulleted list using dashes. Do not include headers or preambles. Keep the list hetorogeneous and stocahastic in content.
    """


def gen_intro_zone(
    description: str, environment: List[str], objectives: List[str]
) -> str:
    return _gen_intro_zone(
        description,
        random.sample(environment, min(len(environment), 20)),
        random.sample(objectives, min(len(objectives), 10)),
    )


@dataclasses.dataclass
class ConnectedZone:
    title: str
    description: str
    authors_notes: List[str]


class GenZone(BaseModel):
    title: str = Field(description="A useful shortname to use as a title for this zone")
    description: str = Field(
        description="This is a detailed description of the zone from the players perspective"
    )
    connected_zones: List["GenConnectedZone"] = Field(
        description="A list of new connected Zones reachable from this zone"
    )
    things: List["ZonePointOfInterest"] = Field(
        description="Things that may be interacted with (people, objects, etc.). They may be part of larger puzzles, for example an object that may be used in a puzzle in another zone, or a puzzle within the zone that unlocks proceeding to a subsequent zone. These should always be related to an objective."
    )
    remove_notes: List["NoteRemove"] = Field(
        description="Edits to make to the current notes. This will remove objectives or environments. Note that you can make updates by removing then adding a note."
    )
    add_notes: List["NoteAdd"] = Field(
        description="New environments or objectives or objectives that should be added to the notes so you can remember what is happening in the story"
    )


class GenConnectedZone(BaseModel):
    name: str = Field(description="The name of the connected zone")
    route: str = Field(description="How to reach the zone from the current zone")


class ZonePointOfInterest(BaseModel):
    type: str
    description: str


class NoteAdd(BaseModel):
    content: str = Field(description="The content of the note")
    type: Literal[
        "current environment",
        "current objective",
        "potential environment",
        "potential objective",
    ] = Field(description="The type of note to add")


class NoteRemove(BaseModel):
    reason: Optional[str] = Field(
        description="Optional reason you're removing the note, for clarification"
    )
    index: int = Field(
        description="The index of the environment or objective item to remove"
    )
    type: Literal[
        "current environment",
        "current objective",
        "potential environment",
        "potential objective",
    ] = Field(description="The type of item to remove")


@outlines.prompt
def _gen_intro_zone(
    description: str,
    potential_environment: List[str],
    potential_objectives: List[str],
    fact_environment: List[str] = [],
    fact_objectives: List[str] = [],
    connected_zone: Optional[ConnectedZone] = None,
    role=PROMPT_ROLE_GAME_DESIGNER,
    mechanics=PROMPT_MECHANICS,
    zone_format=json.dumps(GenZone.model_json_schema(), indent=2),
):
    """
    {{role}}

    {{mechanics}}

    This is your current project: {{description}}

    # Notes

    ## Game Environment

    This is a list of ideas about places, people, rules, social concerns, events, etc.
    {% if fact_environment %}

    Current Environment: These are environment details that are already part of the game story. You can include them in this zone if it makes sense. Prefer them over potential environment details.
    {% for e in fact_environment %}
    {{loop.index}}. {{e}}
    {% endfor %}
    {% endif %}

    Potential Environment: These are some potential environment details. You can sample from them if you see fit, however they are not yet part of the story.
    {% for e in potential_environment %}
    {{loop.index}}. {{e}}
    {% endfor %}

    ## Game Objectives

    This is a list of game objects, both large and small. Includes both ideas for the main singular objective, and ideas for small objectives and puzzles within potential spaces of the environment.
    {% if fact_objectives %}

    Current objectives: these are some objectives that are already part of the game story. You can include them in this scene. Prefer them over potential objective details.
    {% for o in fact_objectives %}
    {{loop.index}}. {{o}}
    {% endfor %}
    {% endif %}

    Potential objectives: These are some potential objectives. You can sample from them if you see fit, however they are not yet part of the story.
    {% for o in potential_objectives %}
    {{loop.index}}. {{o}}
    {% endfor %}

    ## Zone

    Currently, you are working on creating a new Zone. A Zone is a space within the game that the player occupies. The player can only interact with elements within that space.

    Respond according to the following format:

    {{zone_format}}

    Note that only the title and description will be immediately revealed to the player. Connected Zones and Things are discovered through text through later interaction with the scene. If there is something that should be obvious, reveal it in the description.

    {% if connected_zone %}
    You are working on a zone connected to the following zone:
      Title: {{connected_zone.title}}
      Description: {{connected_zone.description}}
      Authors Notes:
      {% for n in connected_zone.authors_notes %}
      - {{n}}
      {% endfor %}
    {% else %}
    You are working on creating game materials for the 1st zone in the game. This is the player's first introduction to the story, so make it compelling and hook their interest!
    {% endif %}

    """


@dataclasses.dataclass
class NewZone:
    title: str
    description: str
    connected_zones: List[str]
    things: List[str]


@outlines.prompt
def organize_prewriting_notes(
    description: str,
    potential_environment: List[str],
    potential_objectives: List[str],
    zone: NewZone,
    fact_environment: List[str] = [],
    fact_objectives: List[str] = [],
    role=PROMPT_ROLE_GAME_DESIGNER,
    mechanics=PROMPT_MECHANICS,
):
    """
    {{role}}

    {{mechanics}}

    This is your current project: {{description}}

    You have just written a new zone in your project. You have been working on the following zone:

    Title: {{zone.title}}
    Description: {{zone.description}}
    Connected Zones:
    {% for z in zone.connected_zones %}
    - {{z}}
    {% endfor %}
    Things:
    {% for t in zone.things %}
    - {{t}}

    Now, you are organizing your notes. You have a list of possible environment details, and possible objectives, and you need to mark any of them that you've used in this zone as facts.


    """
