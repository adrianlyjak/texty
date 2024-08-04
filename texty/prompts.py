from dataclasses import dataclass
import json
from typing import List, Literal, Optional
from bs4 import BeautifulSoup
import outlines
from pydantic import BaseModel, Field, TypeAdapter

from texty.gametypes import (
    GameElement,
    LogItem,
    TimeNode,
    PremiseDraft,
    TypelessGameElement,
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
def prompt_gen_premises(
    n_clues: int = 5,
    n_premises: int = 5,
    user_request: str = "[No requests, generate unique and engaging premises]",
):
    """
    You are building an AI powered interactive story game, similar to classic choose-your-own-adventure books, but with more potential for player agency. To that end, we need to brainstorm {{n_premises}} story premise{% if n_premises != 1 %}s{% endif %}.

    A premise is composed of 4 parts:

    1. The central "Story Problem": This is the main conflict that the story is about. This problem should be made clear to the player from the very beginning, along with some initial choices that will provide the player with some ideas how they can begin to solve the problem. What is the initial suggested course of action?

    2. The "Hidden Clues": In solving the story problem, the player will need to explore the world of the story and uncover clues that will ultimately help them uncover the story's mystery and solve the story problem. There may be many, but describe the {{n_clues}} most important clue{% if n_clues != 1 %}s{% endif %} that they will need to discover in order to reveal the true nature of the story problem and the secret to how to solve it. Describe each clue in detail as well as the impact it will have on the players understanding of the story and it's solution.

    3. The "Surprise Twist": When the player has successfully accumulated all of the clues and is ready to solve the story problem, the story takes a surprising turn that subverts the player's expectations of the true nature of the story problem and its solution.

    4. The "Ultimate Resolution": How does the story end? What does the player ultimately discover about the world? With all the clues successfully assembled, what final action and/or challenge will the player need to take to resolve the story problem? How does the story end?

    For the premises that are being generated now, the user has requested the following:
    <UserRequest>
    {{user_request}}
    </UserRequest>

    Use plain text within XML tags. Avoid markdown and numbered or bulleted lists. Respond in the following XML format, with each premise wrapped in a <Premise> tag:

    <Premise>
    <StoryProblem>
    The story problem
    </StoryProblem>
    <HiddenClues>
    <Clue>
    The first hidden clue. Impact: the impact that it makes
    </Clue>
    <Clue>
    The second hidden clue. Impact: the impact that it makes
    </Clue>
    </HiddenClues>
    <SurpriseTwist>
    The surprise twist
    </SurpriseTwist>
    <UltimateResolution>
    The ultimate resolution
    </UltimateResolution>
    </Premise>
    """


def parse_premises_first_draft(premise_response: str) -> List[PremiseDraft]:
    soup = BeautifulSoup(premise_response, "html.parser")
    premise_elements = soup.find_all("premise")
    return [
        PremiseDraft(
            story_problem=premise.storyproblem.text.strip(),
            hidden_clues=[
                TypelessGameElement(id=f"clue-{i}", text=clue.text.strip())
                for i, clue in enumerate(premise.hiddenclues.find_all("clue"))
            ],
            surprise_twist=premise.surprisetwist.text.strip(),
            ultimate_resolution=premise.ultimateresolution.text.strip(),
        )
        for premise in premise_elements
    ]


@outlines.prompt
def prompt_gen_second_draft_premise(
    story_problem: str,
    hidden_clues: List[str],
    surprise_twist: str,
    ultimate_resolution: str,
    user_request: str = "[No requests, generate unique and engaging premises]",
    n_clues_min: int = 5,
    n_clues_max: int = 15,
    n_elements_min: int = 10,
    n_elements_max: int = 20,
):
    """
    You are an expert story game designer. You are revising a story concept, fleshing it out and improving it.

    The initial story request provided by the player is the following:

    <UserRequest>
    {{user_request}}
    </UserRequest>

    The story concept so far is made up of the following parts:

    <StoryProblem>{{story_problem}}</StoryProblem>
    <HiddenClues>
    {% for clue in hidden_clues %}
    <Clue>{{clue}}</Clue>
    {% endfor %}
    </HiddenClues>
    <SurpriseTwist>{{surprise_twist}}</SurpriseTwist>
    <UltimateResolution>{{ultimate_resolution}}</UltimateResolution>

    You are now building out a revised and fleshed out model of the story. Add more details to each section. You may edit out details from the first draft to make a better and more cohesive narrative in the second draft.

    Unless otherwise noted, none of this information you write will be visible to the player. This is all internal state that the AI will track in order to build a cohesive, engaging, and immersive narrative

    Respond with a repeat of the original input tags, along with some new additional fields. Use XML tags to delimit fields. Respond with all of the following tags:

    <Critique>
    Critique the original story. What works? What doesn't work? What would make it better? This will inform your edits.

    Keep in mind the following:
    - Is anything vague or unclear? Make things specific or remove them.
    - Are there any plot holes or inconsistencies?
    - Does each story tag fit it's definition?
    </Critique>
    <StoryProblem>
    The story problem is the main conflict that the game is about. This problem should be made clear to the player from the very beginning, along with some initial choices that will provide the player with some ideas how they can begin to solve the problem. What is the initial suggested course of action? The story problem should make clear why the character personally cares about the problem, as well as the overall stakes.

    Expand and edit the original according to the critique.
    </StoryProblem>
    <HiddenClues>
    <Clue id="unique-kebab-case-clud-id">
    In solving the story problem, the player will need to explore the world of the story and uncover clues that will ultimately help them uncover the story's mystery and solve the story problem. There may be many, but describe the most important clues that they will need to discover in order to reveal the true nature of the story problem and the secret to how to solve it. Describe each clue in detail as well as the impact it will have on the players understanding of the story and it's solution.
    </Clue>
    <Clue id="the-second-clue">
    Determine a fresh new list of clues based on what you like about the first draft. You may add and expand some of the previous clues only if they are relevant and very high quality.

    Respond with each clue in a separate element. Generate {{n_clues_min}} to {{n_clues_max}} clues total. Stop generating clues before they stop adding value and become repetitive or far fetched.
    </Clue>
    </HiddenClues>
    <PromiseOfThePremise>
    <Opportunity id="unique-kebab-case-opportunity-id">
    Given the story type and world, come up with story elements and opportunities that a reader would expect in this type of story. First explain what the user expects and generally how this element fulfills it. Then make it specific. Make up a character, place, or event that would be expected in this type of story.
    </Opportunity>
    <Opportunity id="the-second-opportunity">
    Respond with between {{n_elements_min}} and {{n_elements_max}} story elements total. Stop generating opportunities before they stop adding value and become repetitive or far fetched.
    </Opportunity>
    </PromiseOfThePremise>
    <SurpriseTwist>
    When the player has successfully accumulated all of the clues and is ready to solve the story problem, the story takes a surprising turn that subverts the player's expectations of the true nature of the story problem and its solution.

    Expand and edit the original according to the critique.
    </SurpriseTwist>
    <UltimateResolution>
    The "Ultimate Resolution" describes how does the story ends. What does the player ultimately discover about the world? With all the clues successfully assembled, what final action and/or challenge will the player need to take to resolve the story problem?

    Expand and edit the original according to the critique.
    </UltimateResolution>
    <GameState>
    Using the scene and sequel methodology, describe whether the game should start in an action or reaction state. (jumping into the action, or starting with background introspection). Respond with only the text "Action" or "Reaction" within the xml GameState tag.
    </GameState>
    <Introduction>
    Write the initial scene for the player here. This will be passed verbatim to the player. This is their first interaction with the game. Make sure that it's immersive, and explains the story context enough to engage the player in exploration and interaction.

    If the <GameState> is "Action" then kick the story off with a bang, requiring the player to act on their feet. Otherwise, if the <GameState> is "Reaction" then keep the game exploratory and introspective, slowly revealing background information that will inform the progression to the next Action.

    Keep in mind the following for good writing:
    - Show don't tell.
    - This is a game, use 3rd person present tense.
    - Take time to establish a clear status quo before introducing the story problem. Do not divulge the full story problem in the introduction. Wait for the player's input before revealing more. The story problem should always be revealed piecemeal over the course of several turns of player/game response. DO NOT DIVULGE THE MAIN STORY PROBLEM. Only tease at its edges. Remember to give the player character smaller more mundane goals to focus on while the main story goals are being established over the course of hundreds of turns of player/game response.
    - Describe sensory details that flesh out the space.
    - Describe the player character's inner state, for example if they are excited, nervous, etc. The player character's inner state will inform the sensory details that they notice.
    - If there are other characters, there should always be dialogue. This dialogue can either inform the story, or else be textural flavor.

    Note that the game ONLY controls external elements. The game NEVER controls the movement, speech, or actions of the player character THIS IS COMPLETELY OFF LIMITS. The player must be prompted for the player character's actions.
    </Introduction>
    <GameElements>
    <Element id="each-element-has-a-unique-readable-kabob-case-id">
    A game element is a concrete "actor" in the story that already exists. For example: a character, object, place, event, etc. Frequently "Opportunity" or "Clue" elements become a game "Element" after they are introduced to the player. Only define elements that have been introduced to the player character, for example in the text of the "Introduction"

    Game element descriptions are not visible to the player. Describe and keep track of internal motivations or backstory for the elements here. You may sample from these details as you further develop the story writing, for example in future dialogue or scenes.
    </Element>
    <Element>
    For this draft, establish any game elements that are needed to make the story introduction feel rich.
    </Element>
    </GameElements>
    """


def parse_premise_second_draft(premise_response: str) -> PremiseDraft:
    soup = BeautifulSoup(premise_response, "html.parser")
    return PremiseDraft(
        critique=soup.critique.text.strip(),
        story_problem=soup.storyproblem.text.strip(),
        hidden_clues=[
            TypelessGameElement(id=clue.attrs["id"], text=clue.text.strip())
            for clue in soup.hiddenclues.find_all("clue")
        ],
        surprise_twist=soup.surprisetwist.text.strip(),
        ultimate_resolution=soup.ultimateresolution.text.strip(),
        opportunities=[
            TypelessGameElement(
                id=opportunity.attrs["id"], text=opportunity.text.strip()
            )
            for opportunity in soup.promiseofthepremise.find_all("opportunity")
        ],
        game_state=soup.gamestate.text.strip(),
        introduction=soup.introduction.text.strip(),
        game_elements=[
            TypelessGameElement(id=element.attrs["id"], text=element.text.strip())
            for element in soup.gameelements.find_all("element")
        ],
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
    game_log: str,
    preamble: str = game_system_prompt(),
):
    """
    {{preamble}}

    ## Instructions

    You are now detecting the intent of the player input. The intent is one of "act", "inspect", or "other".

    "inspect": The player is trying to interact inquisitively with the game system: For example asking a question about the game, or getting details about the observable game state. Look for keywords like: how, what, why, look, inspect, where, read, ask. In response, the game will provide information about the game, doing some basic extrapolation about what would be realistic to the scenario, without affecting change or time advancing (e.g. no travel occurs, just auditory and visual descriptions of the world). The player may only interact with their immediate environment, for example around a small room. This is the most common type of request.
    "act": The player is executing a change in the world and thereby has consequences. Actions move the game forward, inherently have a chance of failure that varies depending on the action, and have consequences. This should only be selected if the Player Character could conceivably achieve this action. Action oriented things like opening, calling, walking, running, yelling, and so on. In some instances, specific non-action is considered an action, for example allowing something to happen that is already in motion.
    "ambiguous": You are not sure what the player is intending. The game will respond with a clarifying prompt.
    "other": This should be used for other requests, for example, questions about the rules, requests for hints, attempts to do something impossible, repeating a previously failed action without anything new, or general table talk or meta questions. If selected, the game will gently explain and guide the player to an appropriate intent. Note that the game _should_ allow any action, no matter how stupid or reckless. Those should instead be "act".


    You will respond in the following json format, providing each of the following fields:
    - thought: A thought out single sentence analysis of A) which intent type is most appropriate for the given input, and B) the difficulty of the task given the environment vs the player character's abilities
    - intent: one of the above intents, "inspect", "act", "ambiguous", or "other"
    - chance_success: Only incuded for some "inspect" or "act" intents. If the action is difficult, include a number between 0 and 1, where 1 is 100% chance of success. This chance should take into account the character's inherent abilities. Think of this like a skill check in a table-top RPG
    - early_response: If the intent is 'ambiguous', or 'other', then the response MUST include a prompt with a message to the user to clarify their actions, otherwise for other intents, this field should be left out. If the player is asking about the game in general, prefix your response with "Out of Character: ", and give a reasonable response

    Respond only with the exact json when prompted.

    ## Examples

    Player Input:
    look around

    JSON Response:
    {
    "thought": "The player is observing their environment at a high level. This sounds like a basic inspect",
    "intent": "inspect"
    }

    ---

    Player Input:
    attack goblin with sword

    JSON Response:
    {
    "thought": "The player is now taking action with the sword, however this is perhaps a difficult task since they've never used a sword before",
    "intent": "act",
    "chance_success": 0.25
    }

    ---

    Player Input:
     x

    JSON Response:
    {
    "thought": "It appears the player, perhaps accidentally, input just the characters ' x '",
    "intent": "ambigous",
    "early_response": "I'm sorry, I don't understand. Did you mistype?"
    }

    ---

    Player Input:
    How does this game work?

    JSON Response:
    {
    "thought": "The player is engaging in table-talk about the structure of the game. I will clarify the rules",
    "intent": "other",
    "early_response": "Out of Character: We're playing a open world game. Send me input about your character's actions, and the game will progress the story. Be careful! Not all paths end well"
    }

    ## Context

    Premise:
    {{premise}}

    Game State:
    {{game_elements}}

    {% if game_log %}
    The following is a list of player/game interactions. This is the only data that the player can see:
    {{game_log}}
    {% endif %}

    Player Input:
    {{player_action}}

    JSON Response:
    """


type Intent = Literal["act", "inspect", "ambiguous", "other"]


class IntentDetection(BaseModel):
    thought: str
    intent: Intent
    chance_success: Optional[float] = None
    early_response: Optional[str] = None


@outlines.prompt
def prompt_plan(
    player_action: str,
    intent: str,
    chance_success: Optional[float],
    did_succeed: bool,
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

    The player's input has been classified as having an intent of "{{intent}}". The following is instructions for how you should respond to this type of input

    {% if intent == "inspect" %}
    {{desc_inspect}}
    {% elif intent == "act" %}
    {{desc_act}}
    {% elif intent == "other" %}
    {{desc_other}}
    {% endif %}

    {% endif %}
    The player has just executed the game with this input:
    ```
    {{player_action}}
    ```

    {% if not did_succeed %}
    The player had a {{chance_success}} chance of success at this action. However the action failed! Describe the consequences of the failure.
    {% elif chance_success %}
    The player had a {{chance_success}} chance of success at this action, and the check passed! Describe the consequences of the success.
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
    - Pay close attention to the previous "game" responses in the player/game interaction history. Build responses based on previous concepts, and avoid being repetitive
    - Use response length mindfully. You write in a terse, but readable and immersive style. Only use long responses when there is a lot to communicate or there is a crescendo of action. It's better to write shorter responses, leaving the character to ask followup questions to increase player game interactions

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


LogItemList = TypeAdapter(List[LogItem])


def dump_events(
    time_node: TimeNode,
    recent_events: List[LogItem] = [],
    max_events: Optional[int] = None,
) -> str:
    logs_to_take = (
        time_node.game_log
        if max_events is None
        else time_node.game_log[-1 * max(0, max_events - len(recent_events)) :]
    )
    response = "\n".join([event.model_dump_json(indent=2) for event in logs_to_take])
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
