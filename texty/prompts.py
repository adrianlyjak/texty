import json
from typing import List, Literal, Optional
import outlines
from pydantic import BaseModel, Field, TypeAdapter

from texty.gametypes import (
    Eventuality,
    GameElement,
    LogItem,
    ProgressLog,
    RetiredGameElement,
    TimeNode,
)


##################################
### prompts and state mutation ###
##################################


@outlines.prompt
def game_system_prompt():

    ### TODO describe character interactions, encourage them to rich and with their own motivations.
    ### every character should have their own personality, and be a dynamic force. No character should tag along with the protagonist without divulging inner character, relationships, and conflict. They should say stuff and have observations from their unique perspective

    ## If you're in an important place of interest, encourage forking, divergent paths for the player to explore. (Lead down false dead ends, side quests, and ambivalent ordered clue collection)

    ## Allow the player to do associations. Give clues, and let the player put them together. Do not give progress away for free.

    """
    ## Rules

    You are running a game simulation. The simulation is simple.
    - The game contains a list of game elements, from small to large
    - The game elements are initialized with world state (characters, places, things), and "eventualities", which are possible game directions
    - The game progresses through player/game response loops, either inspecting or acting against the world
    - First, The player probes the game world (their intent classified as "act" or "inspect")
    - At each timestep, the game updates its internal state, progressing eventualities, and updating the world details
    - The game simulates an immersive, but narrative response to the player's actions

    ## Guidelines to the simulation

    - The game should guide the player towards the eventualities with the most gravity considering current circumstances.
    - The game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character.
    - I repeat, the game never proceeds and narrates the actions of the character. THIS IS COMPLETELY OFF LIMITS.
    - The game may divulge backstory of the player character in the form of inner dialogue
    - The game can and should provide past backstory for the player character, to give the player context.
    - Otherwise, the game (and the assistant) only ever acts as the environment, never the player
    - It's very important to note that this game is intentionally open ended. For example, avoid offering the player a list of options for next actions.
    - Most importantly, treat this as a simulation. Keep the world consistent, and frustratingly real.
    - Mundanity is ok. Failure is common. This is an opportunity to explore how these eventualities might come to pass in a real world scenario.
    - Do not allow the player to do whatever they want. Keep in mind physical, world, and time constraints.
    - For requests that don't fit your mental model of the game, respond with brief dull dead end responses. Part of the joy of the game for the player is discovering things. If every interaction is gratifying, the game is very unsatisfying. You want the player to guess what you are thinking, and make it obvious if they get it wrong
    """


class TimeNodeTemplate(BaseModel):
    premise: str = Field(description="What's the premise of this story")
    game_elements: List["GameElement"] = Field(
        description="Planning nodes in the story",
        default_factory=list,
    )


@outlines.prompt
def desc_intent_inspect():
    """
    Inspect - In response to requests of this type, the game will provide information about the game, doing some basic extrapolation about what would be realistic to the scenario, without affecting signifant change or time advancing (e.g. no travel occurs, just auditory and visual descriptions of the world). The player may only interact with his immediate environment, walking short distances, for example around a small room.
    """


@outlines.prompt
def desc_intent_act():
    """
    Act - In response to requests of this type, the game will play out the players action and the game world's response. An action has consequence, and moves the game forward. Actions have a chance of failure that depends on their complexity and the specific context. In some instances, specific non-action is considered an action, for example allowing something to happen that is already in motion.
    """


@outlines.prompt
def desc_intent_other():
    """
    Other - The player has requested an action somewhat outside the normal mechanisms of the game. For example, questions about the rules, trying to do something impossible, repeating a previously failed action without anything new. If selected, the game will helpfully assist the player, gently guiding the player to an appropriate intent: inspecting or a more realistic action. Note that the game _should_ allow any action that is realistically achievable, no matter how stupid or reckless. Those should instead be "act", but perhaps should have negative consequences.
    """


@outlines.prompt
def desc_game_element_python():
    """
    class GameElement():
        element_id: str = Field(description="The unique id for the game element. A readable kebab-case slug")
        name: str = Field(description="A short name of the game element")
        element_type: Literal["character", "object", "place", "eventuality", "theme", "event", "goal", "idea"]
        past: List[str] = Field(description="Backstory of the game element")
        present: List[str] = Field(description="Descriptions of the game element. Includes events that have occurred to the event over the course of the game")
        future: List[str] = Field(description="Directions or goals for this game element. Used for speculative future planning. Conflicting goals with other elements are a primary source of story conflict")
    """


class GamePremise(BaseModel):
    premise: str
    game_elements: List["GameElement"]


@outlines.prompt
def prompt_define_game(
    premise: str, game_element_schema: str = desc_game_element_python()
):
    """
    Given a rough textual premise for a text adventure store, generates a game "seed" according to the game schema.

    Return a json object with the following format:

    ```
    {
        "premise": str,
        "game_elements": List[GameElement]
    }
    ```

    Where a game element is a dictionary that follows the GameElement schema:

    ```python
    {{ game_element_schema }}
    ```

    The following is a definition of the game element types:
    "character" - Includes both NPCs and the player character
    "object" - physical item. Sometimes can be acquired
    "place" - A physical location, large or small (country, field, building, room, etc)
    "eventuality" - Something that may come to pass. These are the primary drivers of the story
    "theme" - abstract ideas, or stylistic choices, genres etc.
    "event" - something that happens at a time and a place
    "goal" - player objective
    "idea" - a play on ideas, perhaps a premise, such as what if some people were magical, or what if people turned into frogs at night

    - Good stories leave details to be made up and explored during the course of the game. Focus on defining boundaries, so focus on defining types such as "eventuality", "theme", "goal", and "idea".
    - Keep in mind that there's no need to define all of "past", "present" or "future" attributes. These are optional, and will be filled in automatically as the game progresses! The field names may be entirely left out if unneeded at the moment. Past sets the scena and the trajectory, present sets the current scene and circumstances that the game starts with, and future, is a specific detail that may come to pass that guides the stories narrative.
    - Your response should be specific, using names and places. Commit! You won't get a chance to revise these elements, only to add to them. Hand-waving is strictly off limits. Just leave that out if you're not sure.

    You are currently working on the following premise:
    {{ premise }}

    Now respond with only the json object in the format above.

    """


@outlines.prompt
def prompt_detect_intent(
    player_action: str,
    premise: str,
    game_elements: str,
    preamble: str = game_system_prompt(),
):
    """
    {{preamble}}

    ## Context

    The premise of the game is:
    {{premise}}

    The current state of the world is:
    {{game_elements}}

    The player has just entered the following input:
    {{player_action}}

    ## Instructions

    You are now detecting the intent of the player input. The intent is one of "act", "inspect", or "other".

    "inspect": The player is trying to interact with the game system, asking a question about the game, or getting details about the observable game state. Basically any question or request of the game world. Look for keywords like: how, what, why, look, inspect, where, read, ask). In response, the game will provide information about the game, doing some basic extrapolation about what would be realistic to the scenario, without affecting change or time advancing (e.g. no travel occurs, just auditory and visual descriptions of the world). The player may only interact with his immediate environment, walking short distances, for example around a small room. This is the most common type of request.
    "act": The player is executing a change in the world and thereby has consequences. Actions move the game forward, inherently have a chance of failure that varies depending on the action, and have consequences. This should only be selected if the Player Character could conceivably achieve this action. Action oriented things like opening, calling, walking, running, yelling, and so on. In some instances, specific non-action is considered an action, for example allowing something to happen that is already in motion.
    "ambiguous": You are not sure what the player is intending. The game will respond with a clarifying prompt.
    "other": This should be used for other requests, for example, questions about the rules, requests for hints, attempts to do something impossible, repeating a previously failed action without anything new, or general table talk or meta questoins. If selected, the game will gently explain and guide the player to an appropriate intent. Note that the game _should_ allow any action, no matter how stupid or reckless. Those should instead be "act".


    Now, respond in the following json format:
    {
      "thought": "a thought out single sentence analysis of which intent type is most appropriate for the given input",
      "intent": "inspect",
      "early_response": "If the intent is 'ambiguous', then the response MUST include a prompt with a message to the user to clarify their actions, otherwise for other intents, this field should be left out.",
    }

    """


type Intent = Literal["act", "inspect", "ambiguous", "other"]


class IntentDetection(BaseModel):
    thought: str
    intent: Intent
    early_response: Optional[str] = None


@outlines.prompt
def prompt_plan(
    player_action: str,
    intent: str,
    premise: str,
    events_json: str,
    retired_game_events_json: str,
    active_game_events_json: str,
    preamble: str = game_system_prompt(),
    desc_inspect: str = desc_intent_inspect(),
    desc_act: str = desc_intent_act(),
    desc_other: str = desc_intent_other(),
    game_element_def: str = desc_game_element_python(),
):
    """
    {{ preamble }}

    ## Instructions

    Given the players actions, play out what has occurred to the world and its actors. You update the game by specifying update events to the `GameElements` of the story. First, review the current `GameElement`s and then, given the players actions, revise them in order to progress the story in response to the players actions

    A game element has the following shape:

    ```
    {{ game_element_def }}
    ```

    In order to update the game, respond as a json object with the following format:

    ```
    {
    // prewriting to plan a response to the players action. This should include details about what the games response was in order to play out the events that have occurred.
    "response_plan": str,
    // a list of updates to the game, can include any number of events of each of the following types
    "events": [
    // a new game element may be added by specifying a game element with all required fields
    {
      "type": "add_game_element",
      "element_id": str,
      "name": str,
      "element_type": str,
      "past": List[str],
      "present": List[str],
      "future": List[str]
    },
    // removes a game element with a reason
    {
      "type": "retire_game_element",
      "element_id": str,
      "retired_reason": str
    },
    // updates and existing game element, targetted by ID. For small changes, strings can be added to the fields, or for larger rewrites, the entire list can be replaced
    {
      "type": "update_game_element",
      "element_id": str,
      "add": {
        "past": Optional[List[str]],
        "present": Optional[List[str]],
        "future": Optional[List[str]]
      },
      "replace": {
        "past": Optional[List[str]],
        "present": Optional[List[str]],
        "future": Optional[List[str]]
      }
    },
    // if the game has reached a conclusion, describe why (is_success is whether the player "won" or "lost"). Game is over after this event is fired
    {
      "type": "end_game",
      "is_success": bool,
      "description": str
    }
    ],
    // finally, a summary of the above set of changes, to be used as a title for this step of the game
    "summary": str
    }
    ```


    Using this schema of updates, you are simulating the game's response to the player's action, and are able to keep a consistent narrative over player actions. You're the author, you write the story, not the player. When responding, first look at your mental model of the world and the story at this particular point in time. Imagine in isolation, the perfect logical branch points of the story. Then imagine the user's request. Does the user's request fit your mental model? If not, provide a "dead end" update. Make it short and bland, subtly hinting at some of your other branches (and perhaps extending their detail while they have your attention).

    Tips:
    - There are only 4 legal types of events: "add_game_element", "retire_game_element", "update_game_element", and "end_game".
    - Remember to make the game engaging. Don't give things away for free, but lead the player in.
    - Use GameElements to build and update long term plans. This lends continuity and progression which makes the game stay interesting.
    - Give NPCs inner life. They have their own perspectives and motivations. Make their stories consistent and interesting.
    - Mix in dialogue where appropriate.
    - The game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character THIS IS COMPLETELY OFF LIMITS.
    - The game should frequently end, for example with death, entrapment, abduction. The player can undo their actions, so seeing abrupt or tragic ends are exciting and add stakes.
    - The game should proceed with small logical steps. If the players actions on the outside world disagree with the GameElements logical consistency, the game should respond with a non-action.
    - Minimal game changes should occur when the player inspects. Use this opportunity to instead plan future motivations.
    - past, present, and future should only be used for important specifics, not for atmospheric writing.
    - Do not add any events if they are not needed. Absolutely avoid superfluous events.


    ## Context

    The premise of the current game is:
    '''
    {{premise}}
    '''

    The following is a list of the current active GameElements:
    ```
    {{active_game_events_json}}
    ```

    {% if retired_game_events_json %}
    The following is list of retired GameElements:
    ```
    {{retired_game_events_json}}
    ```

    {% endif %}
    {% if events_json %}
    The following is a list of player/game interactions. This is the only data that the player can see:
    ```
    {{events_json}}
    ```

    {% endif %}
    The player has just executed the game with this input:
    ```
    {{player_action}}
    ```

    The player's input has been classified as having an intent of "{{intent}}". The following is instructions for how you should respond to this type of input

    {% if intent == "inspect" %}
    {{desc_inspect}}
    {% elif intent == "act" %}
    {{desc_act}}
    {% elif intent == "other" %}
    {{desc_other}}
    {% endif %}

    Now, respond only as json according to the specified format
    """


@outlines.prompt
def prompt_respond_to_action(
    player_action: str,
    intent: str,
    premise: str,
    game_updates_json: str,
    game_elements_prev_json: str,
    events_json: str,
    preamble: str = game_system_prompt(),
    desc_inspect: str = desc_intent_inspect(),
    desc_act: str = desc_intent_act(),
    desc_other: str = desc_intent_other(),
):
    """
    {{preamble}}

    ## Instructions

    You will now be communicating the simulation's internal updates to the player. While you've made a plan, the devil's in the details, you need to write the scene and bring it all together. This is the real writing for the game, your response is the player's only interaction with the world. None of the game update plan is revealed to the player, you are the voice of the story communicating it into an immersive narrative adventure.

    Guidelines
    - Through storytelling, guide the player towards interactions that evolve towards the game's potential future states
    - This is a text adventure game. End your responses with leading indicators, such as cliff-hangers, or prompts for action, or curious questions about things to look at closer
    - If the player is asking about the game in general, prefix your response with "Out of Character: ", and give a reasonable response
    - Pay close attention to the previous "Game" answers: build responses based on previous concepts, and avoid being repetitive

    ## Context

    The premise of the game is:
    '''
    {{premise}}
    '''

    The player's input has been classified as having an intent of "{{intent}}". The following is instructions for how you should respond to this type of input

    {% if intent == "inspect" %}
    {{desc_inspect}}
    {% elif intent == "act" %}
    {{desc_act}}
    {% elif intent == "other" %}
    {{desc_other}}
    {% endif %}

    The following is a list of the game elements before the updates:
    ```
    {{game_elements_prev_json}}
    ```

    {% if events_json %}
    The following is a list of player/game interactions. This is your conversation history, and is the only content that the player can see:
    ```
    {{events_json}}
    ```

    {% endif %}
    The player has just executed the game with this input:
    ```
    {{player_action}}
    ```

    This is your planned update:
    ```
    {{game_updates_json}}
    ```

    Now, respond with the exact text to return to the player:
    """


def dump_time_node(
    time_node: TimeNode,
    id: bool = False,
    event_log: bool = False,
    previous: bool = False,
) -> str:
    exclude = set()
    if not id:
        exclude.add("id")
    if not event_log:
        exclude.add("event_log")
    if not previous:
        exclude.add("previous")
    return time_node.model_dump_json(indent=2, include=premise)


LogItemList = TypeAdapter(List[LogItem])


def dump_events(time_node: TimeNode, recent_events: List[LogItem] = []) -> str:
    response = "\n".join(
        [event.model_dump_json(indent=2) for event in time_node.event_log]
    )
    if len(recent_events):
        response += "\n// --- RECENT ---\n"
        response += "\n".join(
            [event.model_dump_json(indent=2) for event in recent_events]
        )
    return response


def dump_game_elements(game_elements: List[GameElement]) -> str:
    return (
        "[\n"
        + ",\n".join([el.model_dump_json(indent=2) for el in game_elements])
        + "\n]"
    )


def dump_retired_game_elements(game_elements: List[RetiredGameElement]) -> str:
    def dump_one(retired_game_element: RetiredGameElement) -> str:
        return json.dumps(
            {
                "id": retired_game_element.id,
                "retired_reason": retired_game_element.retired_reason,
            }
        )

    return "[\n" + ",\n".join([dump_one(el) for el in game_elements]) + "\n]"
