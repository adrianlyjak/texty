from typing import List, Literal, Optional, Union
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
    premise: str = Field(description="What's the premise of this story")
    # world_summary: List[str] = Field(description="world details")
    summary: str = Field(
        description="A brief summary of what occurred in this time node",
        default="(None)",
    )
    response_plan: Optional[str] = Field(
        default=None,
        description="The games's plan for the next response to the player",
    )
    previous: List[str] = Field(
        default_factory=list,
        description="The ID of the previous time node. First in the list is the root node, last is the parent",
    )
    event_log: List["LogItem"] = Field(
        default_factory=list,
        description="summarizes the historical player actions and story responses in a linear fashion.",
    )
    last_update: Optional["GameElementUpdate"] = Field(
        default=None,
        description="Debug-only, last update to the game elements in the story",
    )
    game_elements: List["GameElement"] = Field(
        description="Planning nodes in the story",
        default_factory=list,
    )
    retired_game_elements: List["RetiredGameElement"] = Field(
        default_factory=list,
    )

    def scenario_id(self) -> str:
        return self.previous[0] if len(self.previous) else self.id

    def apply_update(self, update: "GameElementUpdate") -> "TimeNode":
        self.last_update = update
        for evt in update.events:
            match evt:
                case AddGameElement():
                    print("process add game element", evt)
                    evt: AddGameElement = evt
                    new_element = GameElement(**evt.model_dump())
                    self.game_elements.append(new_element)
                case RetireGameElement():
                    print("process retire game element", evt)
                    evt: RetireGameElement = evt
                    existing = next(
                        (
                            i
                            for i, x in enumerate(self.game_elements)
                            if x.element_id == update.element_id
                        ),
                        None,
                    )
                    if existing is not None:
                        item = self.game_elements.pop(existing)
                        self.retired_game_elements.append(
                            RetiredGameElement(
                                {
                                    "retired_reason": evt.retired_reason,
                                    **item.model_dump(),
                                }
                            )
                        )
                    self.retired_game_elements.append(update.element)
                case UpdateGameElement():
                    evt: UpdateGameElement = evt
                    existing = next(
                        (
                            x
                            for x in self.game_elements
                            if x.element_id == evt.element_id
                        ),
                        None,
                    )
                    if existing is not None:
                        if evt.replace.past:
                            existing.past = evt.replace.past
                        if evt.replace.present:
                            existing.present = evt.replace.present
                        if evt.replace.future:
                            existing.future = evt.replace.future
                        if evt.add.past:
                            existing.past.extend(evt.add.past)
                        if evt.add.present:
                            existing.present.extend(evt.add.present)
                        if evt.add.future:
                            existing.future.extend(evt.add.future)
                case EndGame():
                    pass
                case other:
                    raise ValueError(f"Unknown event type {other}")


class GameElement(BaseModel):
    element_id: str = Field(
        description="The unique id for the game element. A readable kebab-case slug"
    )
    name: str = Field(description="A short name of the game element")
    element_type: Literal[
        "character", "object", "place", "eventuality", "theme", "event", "goal", "idea"
    ]
    past: List[str] = Field(
        description="Backstory of the game element", default_factory=list
    )
    present: List[str] = Field(
        description="Descriptions of the game element. Includes events that have occurred to the event over the course of the game",
        default_factory=list,
    )
    future: List[str] = Field(
        description="Directions or goals for this game element. Used for speculative future planning. Conflicting goals with other elements are a primary source of story conflict",
        default_factory=list,
    )


class RetiredGameElement(GameElement):
    retired_reason: str


class AddGameElement(BaseModel):
    type: Literal["add_game_element"]
    element_id: str
    name: str
    element_type: Literal[
        "character", "object", "place", "eventuality", "theme", "event", "goal", "idea"
    ]
    past: List[str] = Field(default_factory=list)
    present: List[str] = Field(default_factory=list)
    future: List[str] = Field(default_factory=list)


class RetireGameElement(BaseModel):
    type: Literal["retire_game_element"]
    element_id: str
    retired_reason: str


class GameElementUpdate(BaseModel):
    response_plan: str
    events: List[
        Union[AddGameElement, RetireGameElement, "EndGame", "UpdateGameElement"]
    ] = Field(default_factory=list)
    summary: str


class PastPresentFuture(BaseModel):
    past: Optional[List[str]] = None
    present: Optional[List[str]] = None
    future: Optional[List[str]] = None


class UpdateGameElement(BaseModel):
    type: Literal["update_game_element"]
    element_id: str
    add: PastPresentFuture = Field(default_factory=PastPresentFuture)
    replace: PastPresentFuture = Field(default_factory=PastPresentFuture)


class EndGame(BaseModel):
    type: Literal["end_game"]
    is_success: bool
    description: str


class LogItem(BaseModel):
    role: Literal["player", "game", "internal"]
    type: Literal["act", "inspect", "other", "ambiguous", "game-response"]
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
