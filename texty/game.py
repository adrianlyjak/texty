from typing import Iterator, List, Literal, Optional, Set, Tuple
import uuid
from pydantic import BaseModel, Field, TypeAdapter

from texty.gametypes import Eventuality, LogItem, ProgressLog, TimeNode
from texty import database, seeds
from texty.models.model import get_client
from texty.prompts import (
    Intent,
    IntentDetection,
    dump_events,
    dump_time_node,
    prompt_detect_intent,
    prompt_inspect_time_node,
    prompt_progress_eventuality,
    prompt_reject_input,
    prompt_run_simulation,
    prompt_summarize_time_node,
)

import logging

logger = logging.getLogger(__name__)


class MissingException(Exception):
    pass


class Game:
    node: Optional[TimeNode] = None
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
            self.node = node
            database.insert_time_node(self.node)

    def step(
        self,
        player_action: str,
    ) -> Iterator["AdvanceTimeProgress"]:
        assert self.node is not None
        updated = self.node
        for event in advance_time(player_action, self.node):
            if type(event) == StatusUpdate and event.updated_time_node:
                updated = event.updated_time_node
            yield event
        database.insert_time_node(updated)

    def undo(self) -> bool:
        """Returns true if the undo was successful, false if it was not possible"""
        previous = database.get_node(id=self.node.previous[len(self.node.previous) - 1])
        if not previous:
            return False
        else:
            self.node = previous
            database.set_active_node(scenario_id=self.scenario_id, node_id=self.node.id)
            return True


class StatusUpdate(BaseModel):
    status: Literal[
        "loading-intent",
        "loaded-intent",
        "evaluating-eventuality",
        "evaluated-eventuality",
        "processing-game-response",
        "summarizing-time-node",
        "summarized-time-node",
        "done",
    ]
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
    eventuality_events = []
    if intent == "act":
        eventualities = []
        if not is_initialization:
            yield StatusUpdate(status="evaluating-eventuality")
            time_node, eventualities = progress_eventualities(time_node, events)
            debug_update = "\n".join(
                [f"{updated.id}: {log.text}" for log, updated in eventualities]
            )
            yield StatusUpdate(
                status="evaluated-eventuality",
                debug=debug_update,
                updated_time_node=time_node,
            )
        time_node, eventualities = (
            (time_node, [])
            if is_initialization
            else progress_eventualities(time_node, events)
        )

        for log, eventuality in eventualities:
            eventuality_events.append(
                LogItem(
                    role="game",
                    type="eventuality-progress",
                    text=f"{eventuality.id}: {log.text}",
                    timestep=timestep,
                )
            )
        yield StatusUpdate(status="processing-game-response")
        response = ""
        for update in run_simulation(time_node, events + eventuality_events):
            response += update
            yield TextResponse(full_text=response, delta=update)
        events.append(
            LogItem(role="game", type="game-response", text=response, timestep=timestep)
        )

    elif intent == "inspect":
        yield StatusUpdate(status="processing-game-response")
        response = ""
        for update in inspect_time_node(player_action, time_node):
            response += update
            yield TextResponse(full_text=response, delta=update)
        events.append(
            LogItem(role="game", type="game-response", text=response, timestep=timestep)
        )
    else:
        yield StatusUpdate(status="processing-game-response")
        response = ""
        for update in reject_input(player_action, time_node):
            response += update
            yield TextResponse(full_text=response, delta=update)
        events.append(
            LogItem(role="game", type="game-response", text=response, timestep=timestep)
        )

    yield StatusUpdate(status="summarizing-time-node")
    time_node = summarize_time_node(time_node, events + eventuality_events)

    yield StatusUpdate(status="summarized-time-node", updated_time_node=time_node)
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
        prompt_detect_intent(player_action, dump_time_node(time_node)), IntentDetection
    )


def inspect_time_node(input: str, time_node: TimeNode) -> Iterator[str]:
    """
    A player inspects the current state of the game
    """

    result = get_client("large").stream(
        prompt_inspect_time_node(
            input,
            dump_time_node(time_node),
            dump_events(time_node),
        )
    )
    return result


def reject_input(input: str, time_node: TimeNode) -> Iterator[str]:
    """
    The player has entered an input that is not appropriate for the current context.
    """
    result = get_client("large").stream(
        prompt_reject_input(input, dump_time_node(time_node), dump_events(time_node))
    )
    return result


def progress_eventualities(
    time_node: TimeNode, events: List[LogItem]
) -> Tuple[TimeNode, List[Tuple[ProgressLog, Eventuality]]]:
    """
    Trigger eventuality events based on the player's action
    """
    local_events: List[ProgressLog] = []
    to_remove = []
    update = time_node.model_copy(deep=True)

    excluded = [e for e in update.eventualities if not e.is_complete]
    story_json = dump_time_node(update.model_copy(update={"eventualities": excluded}))
    prompt = prompt_progress_eventuality(
        story_json,
        dump_events(time_node, events + local_events),
    )
    triggers: EventualityTriggers = get_client("large").json(
        prompt, EventualityTriggers
    )
    for trigger in triggers.triggered:
        eventuality = [x for x in excluded if x.id == trigger.id]
        eventuality = eventuality[0] if len(eventuality) else None
        if eventuality:
            eventuality.is_complete = trigger.completed or trigger.delete
            if trigger.delete:
                to_remove.append(eventuality.id)
            log = ProgressLog(
                timestep=time_node.timestep,
                text=(
                    "Completed: "
                    if trigger.completed
                    else "Deleted: " if trigger.delete else ""
                )
                + trigger.progress_log,
            )
            eventuality.progress_log = eventuality.progress_log + [log]
            local_events.append((log, eventuality))
    if to_remove:
        update.eventualities = [
            e for e in update.eventualities if e.id not in to_remove
        ]

    # additions = EventualityList.validate_json(
    #     prompt_add_eventuality(update, events + local_events)
    # )
    # if additions is not None:
    #     update.eventualities = update.eventualities + additions

    return update, local_events


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


def run_simulation(time_node: TimeNode, events: List[LogItem]) -> Iterator[str]:
    prompt = prompt_run_simulation(
        dump_time_node(time_node),
        dump_events(time_node, events),
    )
    # Todo - inject or prompt such that actions aren't immediately gratified. Especially for things like travel events, express the passage of time by injecting pauses, such as an event on a walk, or a conversation in a vehicle.

    return get_client("large").stream(prompt)


def summarize_time_node(time_node: TimeNode, events: List[LogItem]) -> TimeNode:
    """
    Adds new summary to the time node
    """
    update = time_node.model_copy(deep=True)
    prompt = prompt_summarize_time_node(
        dump_time_node(time_node),
        dump_events(time_node, events),
    )
    response = get_client("small").text(prompt)
    update.summary = response
    return update


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
