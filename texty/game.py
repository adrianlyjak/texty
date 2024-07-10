from typing import Iterator, List, Literal, Optional, Set, Tuple
import uuid
from pydantic import BaseModel, Field, TypeAdapter

from texty import prompts
from texty.prompts import (
    Intent,
    IntentDetection,
)

from texty.gametypes import (
    Eventuality,
    GameElementUpdate,
    LogItem,
    ProgressLog,
    TimeNode,
)
from texty import database, seeds
from texty.models.model import get_client

import logging

logger = logging.getLogger(__name__)


class MissingException(Exception):
    pass


class Game:
    node: Optional[TimeNode] = None
    last_node: Optional[TimeNode] = None
    scenario_id: str

    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id

    def start_if_not_started(
        self, seed: TimeNode = seeds.zantar
    ) -> Iterator["AdvanceTimeProgress"]:
        """returns true if the game was started, false if it was already running"""
        self.node = database.get_active_node(scenario_id=self.scenario_id)
        if not self.node:
            node = seed.model_copy(update={"id": self.scenario_id})
            for event in advance_time(
                "(the player has entered. Set the scene for them, imagine a starting scene, and introduce the character and the story)",
                node,
                is_initialization=True,
            ):
                if type(event) == StatusUpdate and event.updated_time_node:
                    node = event.updated_time_node
                yield event
            self.last_node = self.node
            self.node = node
            database.insert_time_node(self.node)

    def step(
        self,
        player_action: str,
    ) -> Iterator["AdvanceTimeProgress"]:
        assert self.node is not None
        previous = self.node
        updated = None
        for event in advance_time(player_action, self.node):
            if type(event) == StatusUpdate and event.updated_time_node:
                updated = event.updated_time_node
                self.last_node = previous
                self.node = updated
                database.insert_time_node(updated)
            yield event
        if updated is None:
            logger.warn("something's wrong, no node updated")

    def undo(self) -> bool:
        """Returns true if the undo was successful, false if it was not possible"""
        node_ids = self.node.previous[-2:]
        previous = database.get_node(id=node_ids[-1]) if len(node_ids) > 1 else None
        preprevious = database.get_node(id=node_ids[-2]) if len(node_ids) > 2 else None
        if not previous:
            return False
        else:
            self.node = previous
            self.last_node = preprevious
            database.set_active_node(scenario_id=self.scenario_id, node_id=self.node.id)
            return True


class StatusUpdate(BaseModel):
    status: str
    updated_time_node: Optional[TimeNode] = None
    debug: Optional[str] = None


class TextResponse(BaseModel):
    full_text: str
    delta: str


AdvanceTimeProgress = StatusUpdate | TextResponse


def advance_time(
    player_action: str, time_node: TimeNode, is_initialization: bool = False
) -> Iterator[AdvanceTimeProgress]:
    """
    An iteration of the game loop
    """
    original = time_node
    time_node = time_node.model_copy(deep=True)
    time_node.id = str(uuid.uuid4())
    time_node.previous = original.previous + [original.id]

    detected_intent: Optional[IntentDetection] = None
    if not is_initialization:
        yield StatusUpdate(status="loading-intent")
        detected_intent = detect_intent(player_action, time_node)
        yield StatusUpdate(
            status="loaded-intent",
            debug=f"{detected_intent.intent}: {detected_intent.thought}",
        )

    intent: Intent = detected_intent.intent if detected_intent else "act"
    if intent == "act":
        time_node.timestep = time_node.timestep + 1
    timestep = time_node.timestep

    events = [
        LogItem(type=intent, role="player", text=player_action, timestep=timestep)
    ]
    if intent == "ambiguous":
        response = (
            detected_intent.early_response if detected_intent is not None else None
        )
        response = (
            response
            or "I'm unsure what your intent is. Can you clarify with either an inspect or an act command?"
        )
        yield TextResponse(full_text=response, delta=response)
        events.append(
            LogItem(
                role="game",
                type="game-response",
                text=response,
                timestep=timestep,
            )
        )
    else:
        plan_prompt = prompts.prompt_plan(
            player_action=player_action,
            intent=intent,
            premise=time_node.premise,
            events_json=prompts.dump_events(time_node),
            retired_game_events_json=prompts.dump_retired_game_elements(
                time_node.retired_game_elements
            ),
            active_game_events_json=prompts.dump_game_elements(time_node.game_elements),
        )
        yield StatusUpdate(status="running-simulation")
        update = get_client("large").json(plan_prompt, GameElementUpdate)
        yield StatusUpdate(status="ran-simulation")
        yield StatusUpdate(status="generate-response")
        prompt = prompts.prompt_respond_to_action(
            player_action=player_action,
            intent=intent,
            premise=time_node.premise,
            game_updates_json=update.model_dump_json(indent=2),
            game_elements_prev_json=prompts.dump_game_elements(time_node.game_elements),
            events_json=prompts.dump_events(time_node),
        )
        response = ""
        for chunk in get_client("large").stream(prompt):
            response += chunk
            yield TextResponse(full_text=response, delta=chunk)
        yield StatusUpdate(status="generated-response")
        events.append(
            LogItem(role="game", type="game-response", text=response, timestep=timestep)
        )
        time_node.last_update = update
        time_node.summary = update.summary
        time_node.apply_update(update)
        # some sort of issue with nulls or something that this fixes
        time_node = TimeNode.model_validate(time_node.model_dump())

    # ignore the seed event, just useful for communicating context for the first iteration
    time_node.event_log = time_node.event_log + (
        events[1:] if is_initialization else events
    )
    yield StatusUpdate(status="done", updated_time_node=time_node)
    return time_node


##################################################
### LLM powered state transformation functions ###
##################################################


def detect_intent(player_action: str, time_node: TimeNode) -> "IntentDetection":
    """
    Given a player response, detect whether its a executable action or an exploratory request.
    If its an exploratory request, fill out the area/world details, and re-request the user for action
    """
    # TODO: consider allowing introspection as part of inspect (or its own intent?). Consider whether dialog should be its own intent.

    return get_client("large").json(
        prompts.prompt_detect_intent(
            player_action,
            time_node.premise,
            prompts.dump_game_elements(time_node.game_elements),
        ),
        IntentDetection,
    )


EventualityList = user_list_adapter = TypeAdapter(Optional[List[Eventuality]])


class EventualityTrigger(BaseModel):
    id: str = Field(description="The eventuality id to trigger")
    progress_log: str = Field(
        description="Update about the player's progress or completion towards the eventuality"
    )
    completed: bool = Field(
        description="Set to true if the eventuality is now complete!"
    )
    delete: bool = Field(
        description="Set to true if the eventuality is now unreachable and should be removed"
    )


class EventualityTriggers(BaseModel):
    triggered: List[EventualityTrigger]


# def update_characters(time_node: TimeNode, events: List[LogItem]) -> TimeNode:
#     """
#     Update the characters (descriptions, relationships) in the story based on the current state of the world and the player's action
#     """
#     # TODO - prompt for the character updates
#     return time_node


# def update_world_details(time_node: TimeNode, events: List[LogItem]) -> TimeNode:
#     """
#     Update the world details
#     """
#     # TODO - prompt for the world updates
#     return time_node
