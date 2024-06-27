from typing import List, Literal
from pydantic import BaseModel, Field


class TimeNode(BaseModel):
    """
    A time node in the story. After each player action, a new node is spawned, with the previous node as the parent. possible_fates, characters, and event histories are copied and updated from the previous node. A player may reload a time node, and start playing a different graph.
    """

    id: str = Field(
        description="The ID of the time node. This is an auto generated UUID"
    )
    timestep: int = Field(
        description="The number of player/game response turns that have occurred",
        default=0,
    )
    summary: str = Field(
        description="A summary of the time node. This is a short description of the time node, the player's lates action, and the systems latest response",
        default="(None)",
    )
    premise: str = Field(description="What's the premise of this story")
    # world_summary: List[str] = Field(description="world details")
    previous: List[str] = Field(
        default_factory=list,
        description="The ID of the previous time node. First in the list is the root node, last is the parent",
    )
    eventualities: List["Eventuality"] = Field(
        default_factory=list,
        description="Game goals and obstacles",
    )
    event_log: List["LogItem"] = Field(
        default_factory=list,
        description="summarizes the player actions and story occurences in a linear fashion.",
    )
    # characters: List["Character"] = Field(
    #     default_factory=list,
    #     description="story relationships",
    # )

    def scenario_id(self) -> str:
        return self.previous[0] if len(self.previous) else self.id


class LogItem(BaseModel):
    role: Literal["player", "game", "internal"]
    type: Literal["act", "inspect", "other", "game-response", "eventuality-progress"]
    text: str
    timestep: int = Field(
        description="The incrementing timestep of the game when this event occurred"
    )


class Eventuality(BaseModel):
    """
    An "Eventuality" is a potential destination that the story tracks. The game drives the player's choices to affect its progression towards an eventuality, and rejects irrelevant actions.
    """

    description: str = Field(
        description="What may come to pass, its affect on the game"
    )
    title: str = Field(description="A human readable title of this eventuality")
    id: str = Field(description="A readable, unique, kebab-case slug")
    ends_game: bool = Field(
        description="True if this eventuality ends the game when it is triggered",
        default=False,
    )
    is_complete: bool = Field(
        description="Completed eventualities are kept around for reference",
        default=False,
    )

    progress_log: List["ProgressLog"] = Field(
        description="Precluding events of this eventuality that have been triggered in the progression of the story.",
        default_factory=list,
    )


class ProgressLog(BaseModel):
    timestep: int
    text: str


class Character(BaseModel):

    name: str = Field(description="Full name")
    is_player: bool = Field(description="True if is a Player Character", default=False)
    description: str = Field(description="Backstory, motivations, and associations")
    relationships: List[str] = Field(
        default_factory=list,
        description="Details about this character's relationships with other characters and story goals. Added to as the story progresses",
    )
