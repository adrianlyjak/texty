from dataclasses import dataclass
from typing import List, Literal, Optional, Union
from uuid import uuid4
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
        description="A brief summary of what occurred in this time node",
        default="(None)",
    )

    story_problem: str = Field(description="The story problem")
    surprise_twist: str = Field(description="The surprise twist")
    ultimate_resolution: str = Field(description="The ultimate resolution")

    game_state: Literal["Action", "Reaction"] = Field(
        description="The current game state",
        default="Action",
    )
    response_plan: Optional[str] = Field(
        default=None,
        description="The games's plan for the next response to the player",
    )
    previous: List[str] = Field(
        default_factory=list,
        description="The ID of the previous time nodes. First in the list is the root node, last is the parent",
    )
    game_log: List["LogItem"] = Field(
        default_factory=list,
        description="The historical player actions and story responses in a linear fashion.",
    )
    game_elements: List["GameElement"] = Field(
        description="active game elements and their backstory / inner state",
        default_factory=list,
    )
    opportunities: List["GameElement"] = Field(
        description="opportunities that may be added to the story",
        default_factory=list,
    )

    def scenario_id(self) -> str:
        return self.previous[0] if len(self.previous) else self.id

    @classmethod
    def from_premise(cls, premise: "PremiseDraft") -> "TimeNode":
        return TimeNode(
            id=str(uuid4()),
            timestep=0,
            story_problem=premise.story_problem,
            surprise_twist=premise.surprise_twist,
            ultimate_resolution=premise.ultimate_resolution,
            game_state=premise.game_state,
            game_log=[],
            game_elements=[
                GameElement(
                    id=x.id,
                    element_type="actor",
                    state=x.text,
                )
                for x in premise.game_elements
            ],
            opportunities=[
                GameElement(
                    id=x.id,
                    element_type="premise",
                    state=x.text,
                )
                for x in premise.opportunities
            ],
        )


@dataclass
class PremiseDraft:
    critique: str = Field(default="")
    story_problem: str = Field(default="")
    hidden_clues: List["TypelessGameElement"] = Field(default_factory=list)
    surprise_twist: str = Field(default="")
    ultimate_resolution: str = Field(default="")
    opportunities: List["TypelessGameElement"] = Field(default_factory=list)
    game_state: Literal["Action", "Reaction"] = Field(default="Action")
    # introduction: str = Field(default="")
    game_elements: List["TypelessGameElement"] = Field(default_factory=list)


@dataclass
class TypelessGameElement:
    id: str
    text: str


class GameElement(BaseModel):
    id: str = Field(
        description="The unique id for the game element. A readable kebab-case slug"
    )
    element_type: Literal["clue", "premise", "actor"]
    state: str = Field(description="The inner state of the game element")


class EndGame(BaseModel):
    type: Literal["end_game"]
    is_success: bool
    description: str


class LogItem(BaseModel):
    role: Literal["player", "game"]
    type: Literal["act", "inspect", "other", "ambiguous", "game-response"]
    text: str
    timestep: int = Field(
        description="The incrementing timestep of the game when this event occurred"
    )
