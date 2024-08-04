import random
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterator,
    Optional,
)
import uuid
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, TypeAdapter

from texty import prompts
from texty._async import async_gen_to_blocking_iterator
from texty.prompts import (
    GamePremise,
    Intent,
    IntentDetection,
)

from texty.gametypes import (
    GameElementUpdate,
    LogItem,
    TimeNode,
)
from texty import database, seeds
from texty.llm import get_client

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

    @staticmethod
    async def from_prompt(premise: str) -> TimeNode:
        prompt = prompts.prompt_define_game(premise)
        response = await get_client("large").json(prompt, GamePremise)
        id = str(uuid.uuid4())
        time_node = TimeNode(
            id=id,
            summary="(Game not yet begun)",
            premise=response.premise,
            game_elements=response.game_elements,
        )
        database.insert_time_node(time_node)

        return time_node

    @staticmethod
    def from_seed(seed: str) -> TimeNode:
        time_node = seeds.get_seed(seed)
        id = str(uuid.uuid4())
        time_node = time_node.model_copy(update={"id": id}, deep=True)
        database.insert_time_node(time_node)
        return time_node

    async def start_if_not_started_async(
        self, seed: TimeNode = seeds.zantar
    ) -> AsyncGenerator["AdvanceTimeProgress", None]:
        """returns true if the game was started, false if it was already running"""
        self.node = database.get_active_node(scenario_id=self.scenario_id)
        if not self.node:
            self.node = seed.model_copy(update={"id": self.scenario_id})
        if not self.node.game_log:
            updated = None
            async for event in advance_time_async(
                "(the player has entered. Set the scene for them, imagine a starting scene, and introduce the character and the story)",
                self.node,
                is_initialization=True,
            ):
                if type(event) == TimeNodeUpdate:
                    updated = event.updated_time_node
                yield event
            if updated:
                self.last_node = self.node
            self.node = updated or self.node
            database.insert_time_node(self.node)

    def start_if_not_started(
        self, seed: TimeNode = seeds.zantar
    ) -> Iterator["AdvanceTimeProgress"]:
        return async_gen_to_blocking_iterator(self.start_if_not_started_async, seed)

    async def step_async(
        self,
        player_action: str,
    ) -> AsyncGenerator["AdvanceTimeProgress", None]:
        assert self.node is not None
        previous = self.node
        updated = None
        async for event in advance_time_async(player_action, self.node):
            if type(event) == TimeNodeUpdate:
                updated = event.updated_time_node
                self.last_node = previous
                self.node = updated
                database.insert_time_node(updated)
            yield event
        if updated is None:
            logger.warn("something's wrong, no node updated")

    def step(
        self,
        player_action: str,
    ) -> Iterator["AdvanceTimeProgress"]:
        return async_gen_to_blocking_iterator(self.step_async, player_action)

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


class TimeNodeUpdate(BaseModel):
    updated_time_node: TimeNode


class ProgressUpdate(BaseModel):
    type: str
    progress: float  # 0-1
    details: Optional[Dict[str, Any]] = None


class DiceRoll(BaseModel):
    chance_success: float  # 0-1
    did_succeed: Optional[bool] = None


class TextResponse(BaseModel):
    full_text: str
    delta: str


AdvanceTimeProgress = TextResponse | ProgressUpdate | TimeNodeUpdate | DiceRoll


async def advance_time_async(
    player_action: str, time_node: TimeNode, is_initialization: bool = False
) -> AsyncGenerator[AdvanceTimeProgress, None]:
    """
    An iteration of the game loop
    """
    original = time_node
    time_node = time_node.model_copy(deep=True)
    time_node.id = str(uuid.uuid4())
    time_node.previous = original.previous + [original.id]

    detected_intent: Optional[IntentDetection] = None
    if not is_initialization:
        yield ProgressUpdate(type="detect_intent", progress=0)
        detected_intent = await detect_intent(player_action, time_node)
        yield ProgressUpdate(
            type="detect_intent",
            progress=1,
            details=detected_intent.model_dump(),
        )

    intent: Intent = detected_intent.intent if detected_intent else "act"
    if intent == "act":
        time_node.timestep = time_node.timestep + 1
    timestep = time_node.timestep

    events = [
        LogItem(type=intent, role="player", text=player_action, timestep=timestep)
    ]
    if intent == "ambiguous" or intent == "other":
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
        chance = detected_intent.chance_success if detected_intent else None
        rand = random.random()
        did_succeed = True if chance is None else rand <= chance
        did_succeed_message = "succeeded" if did_succeed else "failed"
        print(f"chance: {chance}, rand: {rand}, did_succeed: {did_succeed}")
        if chance is not None:
            yield DiceRoll(chance_success=chance, did_succeed=None)
        plan_prompt = prompts.prompt_plan(
            player_action=player_action,
            intent=intent,
            did_succeed=did_succeed,
            chance_success=f"{chance * 100:.2f}%" if chance else None,
            premise=time_node.premise,
            events_json=prompts.dump_events(time_node),
            retired_game_events_json=prompts.dump_retired_game_elements(
                time_node.retired_game_elements
            ),
            active_game_events_json=prompts.dump_game_elements(time_node.game_elements),
        )
        # delay the success/failure result while planning the story to add tension
        if chance is not None:
            yield DiceRoll(chance_success=chance, did_succeed=did_succeed)
        yield ProgressUpdate(type="plan_story", progress=0)
        update = await get_client("large").json(plan_prompt, GameElementUpdate)
        yield ProgressUpdate(type="plan_story", progress=1)
        yield ProgressUpdate(type="generate_response", progress=0)
        prompt = prompts.prompt_respond_to_action(
            player_action=player_action,
            intent=intent,
            premise=time_node.premise,
            game_updates_json=update.model_dump_json(indent=2),
            game_elements_prev_json=prompts.dump_game_elements(time_node.game_elements),
            events_json=prompts.dump_events(time_node),
        )
        response = ""
        async for chunk in get_client("large").stream(prompt):
            response += chunk
            yield TextResponse(full_text=response, delta=chunk)
        yield ProgressUpdate(type="generate_response", progress=1)
        events.append(
            LogItem(role="game", type="game-response", text=response, timestep=timestep)
        )
        time_node.last_update = update
        time_node.summary = update.summary
        time_node.apply_update(update)
        # some sort of issue with nulls or something that this fixes
        time_node = TimeNode.model_validate(time_node.model_dump())

    # ignore the seed event, just useful for communicating context for the first iteration
    time_node.game_log = time_node.game_log + (
        events[1:] if is_initialization else events
    )
    yield TimeNodeUpdate(updated_time_node=time_node)


def advance_time(
    player_action: str, time_node: TimeNode, is_initialization: bool = False
) -> Iterator[AdvanceTimeProgress]:
    """
    An iteration of the game loop
    """
    return async_gen_to_blocking_iterator(
        advance_time_async, player_action, time_node, is_initialization
    )


##################################################
### LLM powered state transformation functions ###
##################################################


async def detect_intent(player_action: str, time_node: TimeNode) -> "IntentDetection":
    """
    Given a player response, detect whether its a executable action or an exploratory request.
    If its an exploratory request, fill out the area/world details, and re-request the user for action
    """
    # TODO: consider allowing introspection as part of inspect (or its own intent?). Consider whether dialog should be its own intent.

    return await get_client("large").json(
        prompts.prompt_detect_intent(
            player_action,
            time_node.premise,
            prompts.dump_game_elements(time_node.game_elements),
            prompts.dump_events(time_node, max_events=5),
        ),
        IntentDetection,
    )
