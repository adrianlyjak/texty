from typing import List, Literal, Optional
import outlines
from pydantic import BaseModel, Field, TypeAdapter

from texty.gametypes import Eventuality, LogItem, ProgressLog, TimeNode


##################################
### prompts and state mutation ###
##################################


@outlines.prompt
def game_prompt():

    ### TODO describe character interactions, encourage them to rich and with their own motivations.
    ### every character should have their own personality, and be a dynamic force. No character should tag along with the protagonist without divulging inner character, relationships, and conflict. They should say stuff and have observations from their unique perspective

    ## If you're in an important place of interest, encourage forking, divergent paths for the player to explore. (Lead down false dead ends, side quests, and ambivalent ordered clue collection)

    ## Allow the player to do associations. Give clues, and let the player put them together. Do not give progress away for free.

    """
    ## Rules

    You are running a game simulation. The simulation is simple.
    - The game contains a list of hidden potential eventualities
    - The game is initialized with world state
    - The player probes the game world
    - The game progresses through player/game response loops, either inspecting or acting against the world
    - whenever the player acts, a timestep occurs
    - At each timestep, the game updates its internal state, progressing eventualities, and updating the world details
    - The game simulates an immersive, but narrative response to the player's actions

    ## Guidelines to the simulation

    - The game should guide the player through storytelling to the eventualities that have the most gravity in the current circumstances.
    - The game creates a rich, immersive, and consistent world and characters
    - The game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character.
    - I repeat, the game never proceeds and narrates the actions of the character. THIS IS COMPLETELY OFF LIMITS.
    - The game may divulge backstory of the player Character in the form of inner dialogue
    - The game can and should provide past backstory for the player character, to give the player context.
    - Otherwise, the game (and the assistant) only ever acts as the environment, never the player
    - It's very important to note that this game is intentionally open ended. For example, avoid offering the player a list of options for next actions.
    - Most importantly, treat this as a simulation. Keep the world consistent, and frustratingly real.
    - Mundanity is ok. Failure is common. This is an opportunity to explore how these eventualities might come to pass in a real world scenario.
    - Do not allow the player to do whatever they want. Keep in mind physical, world, and time constraints.
    - For requests that don't fit your mental model of the game, respond with brief dull dead end responses. Part of the joy of the game for the player is discovering things. If every interaction is gratifying, the game is very unsatisfying. Be a stubborn challenger, you want the player to guess what you are thinking.
    """


@outlines.prompt
def prompt_detect_intent(
    player_action: str, time_node: str, preamble: str = game_prompt()
):
    """
    {{preamble}}

    ## Context

    The current state of the game is:
    {{time_node}}

    The player has just entered the following input:
    {{player_action}}

    ## Instructions

    You are now detecting the intent of the player input. The intent is one of "act", "inspect", or "other".

    "inspect": The player is trying to interact with the game system, asking a question about the game, or getting details about the observable game state. Basically any question or request of the game world. Look for keywords like: how, what, why, look, inspect, where, read, ask). In response, the game will provide information about the game, doing some basic extrapolation about what would be realistic to the scenario, without affecting change or time advancing (e.g. no travel occurs, just auditory and visual descriptions of the world). The player may only interact with his immediate environment, walking short distances, for example around a small room. This is the most common type of request.
    "act": The player is executing a change in the world. The game will advance one timestep, and world changes will occur. This should only be selected if the Player Character could conceivably achieve this action. Action oriented things like opening, calling, walking, running, yelling, and so on.
    "ambiguous": You are not sure what the player is intending, or they are trying to do too many actions at once. The game will respond with a clarifying prompt.
    "other": This should be used for other requests, for example, questions about the rules, trying to do something impossible, repeating a previously failed action without anything new. If selected, the game will gently explain and guide the player to an appropriate intent. Note that the game _should_ allow any action, no matter how stupid or reckless. Those should instead be "act".


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
def prompt_inspect_time_node(
    input: str, story_json: str, events_json: str, preamble: str = game_prompt()
):
    """
    {{preamble}}

    ## Context

    The current state of the game is:
    ```
    {{story_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    The user input is:
    '''
    {{input}}
    '''


    ## Instructions

    The player is currently inspecting the current world state.

    You're the author, you write the story, not the player. When responding, first look at your mental model of the world and the story at this particular point in time. Imagine in isolation, the perfect logical branch points of the story. Then imagine the user's request. Does the user's request fit your mental model? If not, provide a "dead end" response. Make it short and bland, subtly hinting at one of your branches.
    This is incredibly important to get right. The joy of the game to the player, is to be a sleuth, and they are solving the puzzle that is you.

    During an inspection event, you, the author, will now provide a detailed description of the current world state--without affecting change or advancing time (e.g. no travel occurs, just auditory and visual descriptions of the world)

    Respond to their request succinctly. You are free to creatively make up some state about the world where appropriate, however refrain from giving away any details about state not observable by the player.

    Respond now only with the text to return to the player:
    """


@outlines.prompt
def prompt_reject_input(
    input: str, story_json: str, events_json: str, preamble: str = game_prompt()
):
    """
    {{preamble}}

    ## Context

    The current state of the game is:

    ```
    {{story_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    The rejected user input is:

    '''
    {{input}}
    '''

    ## Instructions

    The player has entered an input that is not quite appropriate for the current context. Gently redirect the user towards a more appropriate intent (inspection or action).

    - If the player has requested something impossible, recommend something that they could do instead.
    - If the player is asking about the rules, give a brief explanation of the relevant rules or an acceptable instruction.
    - If the player is trying to go outside of the bounds of what would further any eventuality, tease some world details or hints, guiding them to re-engage with the given simulation. However don't say or change anything about the story that would affect the game state.

    Now, respond only with the text to return to the player:
    """


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


@outlines.prompt
def prompt_plan(
    player_action: str,
    time_node_json: str,
    events_json: str,
    retired_game_events_json: str,
    active_game_events_json: str,
    preamble: str = game_prompt(),
):
    """
    {{preamble}}

    ## Instructions

    Given the players actions, play out what has occurred to the world and its actors. You update the game by specifying update events to the `GameElements` of the story. First, review the current `GameElement`s and then, given the players actions, revise them in order to progress the story in response to the players actions

    A game element has the following shape:

    ```
    GameElement:
        element_id: str = Field(description="The unique id for the game element. A readable kebab-case slug")
        name: str = Field(description="A short name of the game element")
        type: Literal["character", "object", "place", "eventuality", "theme", "event", "goal", "idea"]
        past: List[str] = Field(description="Backstory of the game element")
        present: List[str] = Field(description="Descriptions of the game element. Includes events that have occurred to the event over the course of the game")
        future: List[str] = Field(description="Directions or goals for this game element. Used for speculative future planning. Conflicting goals with other elements are a primary source of story conflict")
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
      "type": str,
      "past": List[str],
      "present": List[str],
      "future": List[str]
    },
    // removes a game element with a reason
    {
      "type": "retire_game_element",
      "element_id": str,
      "reason": str
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
    // if the game has reached a conclusion, describe why, and end the game
    {
      "type": "end_game",
      "game_end_event": {
        "eventuality_id": str,
        "is_success": bool,
        "description": str
      }
    }
    ]
    }
    ```

    Using this schema of updates, you are simulating the game's response to the player's action, and are able to keep a consistent narrative over player actions.

    Tips:
    - Remember to make the game engaging. Don't give things away for free, but lead the player in.
    - Use GameElements to build and update long term plans. This lends continuity and progression which makes the game stay interesting.
    - Give NPCs inner life. They have their own perspectives and motivations. Make their stories consistent and interesting.
    - Mix in dialogue where appropriate.
    - The game should frequently end, for example with death, entrapment, abduction. The player can undo their actions, so seeing abrupt or tragic ends are exciting and add stakes.
    - The game should proceed with small logical steps. If the players actions on the outside world disagree with the GameElements logical consistency, the game should respond with a non-action.
    - Minimal game changes should occur when the player inspects. Use this opportunity to instead plan future motivations.


    ## Context

    The current state of the game is:
    ```
    {{time_node_json}}
    ```

    The following is list of retired GameElements:
    ```
    {{retired_game_events_json}}
    ```

    The following is a list of player game responses:
    ```
    {{events_json}}
    ```

    The following is a list of the current active GameElements:
    ```
    {{active_game_events_json}}
    ```

    The player has just executed the game with this input:
    ```
    {{player_action}}
    ```

    Now, respond only as json according to the specified format
    """


@outlines.prompt
def prompt_progress_eventuality(
    time_node_json: str,
    events_json: str,
    preamble: str = game_prompt(),
):
    """
    {{preamble}}

    ## Instructions

    You are now evaluating all eventualities against the given circumstances in the context. Creatively consider whether each eventuality was affected by the player's actions. Look at if this eventuality has some sort of inherent ticking clock, and if so, consider if enough timesteps have passed to trigger a story event. There is a careful balance to strike between triggering eventualities too often, and not triggering them enough. Try to pace the story such that it takes around 50 actions to complete. If there is not player action, it's good to at least trigger one eventuality with some sort of backstory that is not immediately visible to the player, but could be soon. This helps build backstory and model the world.

    If nothing has triggered, respond with this json:
    { "triggered": [] }

    If something has triggered, think about the progression of the eventuality, and respond with a creative and specific description of how the eventuality has progressed or completed. This is where you make up game details, clues, characters. If the player has done something dangerous or reckless, considering triggering a premature end to the game.

    Respond with json, with the following format:
    { "triggered": [{ "id": "the-eventuality-id", "progress_log": "A description of how the eventuality has progressed or completed", "completed": false, "delete": false }] }

    Note that the eventuality is considered complete if the "completed" field is true. This may either be due to the eventuality reaching completion. Alternately, if the eventuality is now completely unreachable, and should be removed, set the "delete" field to true.

    ## Context

    The current state of the game is:
    ```
    {{time_node_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    Respond with json, with the following format:
    { "triggered": [{ "id": "the-eventuality-id", "progress_log": "A description of how the eventuality has progressed or completed", "completed": false, "delete": false }] }
    """


@outlines.prompt
def prompt_run_simulation(
    time_node_json: str,
    events_json: str,
    eventuality_events_json: Optional[str],
    preamble: str = game_prompt(),
):
    """
    {{preamble}}

    ## Instructions

    You are now generating a game response to return to the user, simulating the response to their action. This is the real writing for the game, your response is the player's only interaction with the world.

    Closely read the eventualities, and guide the player through storytelling towards the eventualities that have the most gravity in this moment. If the player tries to do irrelevant, reckless, or dumb things without merit, play along, but lead them to a dead end or a premature ending. This will allow you to continue the story, but give the player a sense of autonomy.

    The game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character. I repeat, the game never proceeds and narrates the actions of the character. THIS IS COMPLETELY OFF LIMITS. You may only end your response prompting a user for an action.

    Tips:
    - If any eventuality events just triggered, weave it into the story. The player has not been told about any of these events, so be sure to be explicit if you want the player to know what happened. (Note that some events should not yet be divulged.)
    - If no eventualities triggered, how can you guide the players actions towards any eventualities?
    - Remember to make the game engaging. Don't give things away for free, but lead the player in.
    - Mix in dialogue where appropriate.
    - Give NPCs inner life. They have their own perspectives and motivations. Make their stories consistent and interesting.
    - The game should frequently end, for example with death, entrapment, abduction. The player can undo their actions, so seeing abrupt or tragic ends are exciting.

    ## Context

    The current state of the game is:
    ```
    {{time_node_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    {% if eventuality_events_json %}
    The following is a log of eventuality events that have just occurred (The player has not been informed of these! Make sure to narrate them!):
    ```
    {{eventuality_events_json}}
    ```
    {% endif %}

    ## Instructions

    Now, respond only with the text to return to the player:
    """


@outlines.prompt
def prompt_summarize_time_node(time_node_json: str, events_json: str):
    """
    Return a summary of the current updates to the story, to be displayed as a subject in a list

    This is the current state of the story:
    ```
    {{time_node_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    Respond as a single short sentence with just the summary
    """


def dump_time_node(
    time_node: TimeNode, id=False, event_log=False, previous=False
) -> str:
    exclude = set()
    if not id:
        exclude.add("id")
    if not event_log:
        exclude.add("event_log")
    if not previous:
        exclude.add("previous")
    return time_node.model_dump_json(indent=2, exclude=exclude)


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
