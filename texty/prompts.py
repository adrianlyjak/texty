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
    - The game progresses through player/game response loops (each loop is a timestep)
    - At each timestep, the game updates its internal state, progressing eventualities, and updating the world details
    - The game simulates an immersive, but narrative response to the player's actions

    ## Guidelines to the simulator
    - The game should guide the player through storytelling to the eventualities that have the most gravity in the current circumstances.
    - The game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character.
    - The game (and the assistant) is only the environment, never the player
    - The game can and should provide past backstory for the player character, to give the player context.
    - If the player tries to do irrelevant things, or fails to make progress, do not play along.
    - Always guide them back to the main storyline.
    - It's very important to note that this game is intentionally open ended. For example, avoid offering the player a list of options for next actions
    - Most importantly, treat this as a simulation. Keep the world consistent, and frustratingly real.
    - Do not allow the player to do whatever they want. Keep in mind physical, world, and time constraints.
    - Mundanity is ok. Failure is common. This is an oppurtunity to explore how these eventualities might come to pass in a real world scenario.
    - Respond with brief dull dead end responses, for requests that don't fit your mental model of the game. Part of the joy of the game for the player is discovering things. If every interaction is gratifying, the game is very unsatisfying. Be a stubborn challenger, you want the player to guess what you are thinking.
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

    "inspect": The player is trying to interact with the game system, asking a question about the game, or getting details about the observable game state. Basically any question or request of the game world. Look for keywords like: how, what, why, look, inspect, where, read, ask). In response, the game will provide information about the game, doing some basic extrapolation about what would be realistic to the scenario, without affecting change or time advancing (e.g. no conversations occur, no travel occurs, just auditory and visual descriptions of the world). This is the most common type of request.
    "act": The player is executing a change in the world. The game will advance one timestep, and world changes will occur. This should only be selected if the Player Character could conceivably achieve this action.
    "other": This should be used for other requests, for example, questions about the rules, trying to do something impossible, repeating a previously failed action without anything new, or something that is not appropriate for the current context. If selected, the game will gently explain and guide the player to an appropriate intent.


    Now, respond in the following format:
    {
      "thought": "a thought out single sentence analysis of which intent type is most appropriate for the given input",
      "intent": "inspect"
    }

    """


type Intent = Literal["act", "inspect", "other"]


class IntentDetection(BaseModel):
    thought: str
    intent: Intent


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

    You're the author, your write the story, not the player. When responding, first look at your mental model of the world and the story at this particular point in time. Imagine in isolation, a perfect untouched mental model. Then imagine the user's request. Does the user's request fit your mental model? If not, provide a "dead end" response. Make it short and bland.
    This is incredibly important to get right. The joy of the game to the player, is to be a sleuth, and they are solving the puzzle that is you, and the answer they are trying to find is the perfect game.

    Note also, the game will now provide a detailed description of the current world state, without affecting change or advancing time (e.g. no conversations occur, no travel occurs, just auditory and visual descriptions of the world)

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
def prompt_progress_eventuality(
    time_node_json: str,
    events_json: str,
    preamble: str = game_prompt(),
):
    """
    {{preamble}}

    ## Context

    The current state of the game is:
    ```
    {{time_node_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    ## Instructions

    Now you're evaluating the eventualities against the given circumstances in the context. Creatively consider whether each eventuality was effected. Look at the other events for triggers that may have incited this eventuality, or look at if this eventuality has some sort of inherent ticking clock, and if so, consider if enough timesteps have passed to trigger it's progression. There is a careful balance to strike between triggering eventualities too often, and not triggering them enough. Try to pace the story such that it takes around 50 steps to complete.

    If nothing has triggered, respond with this json:
    { "triggered": [] }

    If something has triggered, think about the progression of the eventuality, and respond with a creative and specific description of how the eventuality has progressed or completed. This is where you make up game details, clues, characters. Respond with json, with the following format:
    { "triggered": [{ "id": "the-eventuality-id", "progress_log": "A description of how the eventuality has progressed or completed", "completed": false, "delete": false }] }

    Note that the eventuality is considered complete if the "completed" field is true. This may either be due to the eventuality reaching completion. Alternately, if the eventuality is now completely unreachable, and should be removed, set the "delete" field to true.
    """


@outlines.prompt
def prompt_run_simulation(
    time_node_json: str, events_json: str, preamble: str = game_prompt()
):
    """
    {{preamble}}

    ## Context

    The current state of the game is:
    ```
    {{time_node_json}}
    ```

    The following is a log of previous events:
    ```
    {{events_json}}
    ```

    ## Instructions

    You are now generating a game response to return to the user, simulating the response to their action. This is the real important part of the game, it's their only interaction with the world.

    The game should guide the player through storytelling to the eventualities that have the most gravity. If the player tries to do irrelevant things, or fails to make progress or solve puzzles, do not play along. Always guide them back to the main storyline.

    Tips:
    - If any eventualities just triggered, weave it into the story.
    - If not, how can you guide the players actions towards any eventualities?
    - Remember to make the game engaging. Don't give things away for free, but lead the player in.

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
