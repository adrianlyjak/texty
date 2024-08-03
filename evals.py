import json
import logging
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import Generate, TaskState, call_tools, generate, solver
from inspect_ai.model import CachePolicy, ChatMessageUser
from texty.gametypes import TimeNode
from texty import seeds
from texty import prompts


@solver
def run_planning(intent: prompts.Intent):
    async def solve(state: TaskState, generate: Generate):
        node: TimeNode = state.metadata["time_node"]
        msg = ChatMessageUser(
            role="user",
            content=prompts.prompt_plan(
                player_action=state.input,
                intent=intent,
                premise=node.premise,
                events_json=prompts.dump_events(node),
                retired_game_events_json="",
                active_game_events_json=prompts.dump_game_elements(node.game_elements),
            ),
        )
        state.messages = [msg]
        state = await generate(state, cache=False)
        json_obj = extract_json_obj(state.output.completion)
        state.metadata["update"] = json_obj
        original_messages = state.messages
        state.messages = [
            ChatMessageUser(
                role="user",
                content=prompts.prompt_respond_to_action(
                    player_action=state.input,
                    intent=intent,
                    premise=node.premise,
                    game_updates_json=extract_json_obj(state.output.completion),
                    game_elements_prev_json=prompts.dump_game_elements(
                        node.game_elements
                    ),
                    events_json=prompts.dump_events(node),
                ),
            )
        ]
        state = await generate(state, cache=CachePolicy(expiry="12M"))
        state.messages = original_messages + state.messages
        return state

    return solve


def extract_json_obj(json_str: str) -> str:
    # find first index of "{" and last index of "}" in json_str
    start_index = json_str.index("{")
    end_index = json_str.rindex("}")
    # parse json_str between the two indices
    json_str = json_str[start_index : end_index + 1]
    return json_str


@task
def eval_planning_from_seed():
    return Task(
        dataset=MemoryDataset(
            samples=[
                Sample(
                    input="(the player has entered. Set the scene for them, imagine a starting scene, and introduce the character and the story)",
                    target="",
                    metadata=dict(time_node=seeds.blackwood_manor),
                )
            ],
        ),
        plan=[
            run_planning("act"),
        ],
    )


@solver
def run_define_game():
    async def solve(state: TaskState, generate: Generate):
        msg = ChatMessageUser(
            role="user",
            content=prompts.prompt_define_game(state.input),
        )
        state.messages = [msg]
        return state

    return solve


@task
def eval_define_game():
    return Task(
        dataset=MemoryDataset(
            samples=[
                Sample(
                    input="In a post-apocalyptic world, the player must navigate a dangerous wasteland filled with mutated creatures and hostile factions in search of a rumored hidden paradise.",
                    target="",
                )
            ],
        ),
        plan=[
            run_define_game(),
            generate(cache=CachePolicy(expiry="12M")),
        ],
    )


from typing import List, Literal, Optional
from pydantic import BaseModel
from inspect_ai.solver import tool, use_tools
from inspect_ai import task, Task


class Word(BaseModel):
    type: Literal["adjective", "noun"]
    word: str


@tool(
    prompt="A defined schema for the structured extraction of words from the input",
    name="extract_words",
)
def my_tool():
    async def extract(words: list) -> str:
        """
        Accepts the extracted nouns and adjectives from the sentence

        Args:
          words: the extract json object words
        Returns: the same structured output passed, for consumption by the application
        """
        print("got input extracted", words)
        return words

    return extract


@solver
def generate_words():
    async def solve(state: TaskState, generate: Generate):
        state.tool_choice = "any"
        state.tools = [my_tool()]
        print(my_tool())
        # setup logger for this source file
        logger = logging.getLogger(__name__)

        # log each time we see a web query
        logger.info(f"web query:{my_tool()}")
        await generate(state, tool_calls="none", cache=False)
        return state

    return solve


@task
def eval_word_extract():
    return Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="Extract the nouns and adjectives from the following sentence.\nSentence:\nThe quick brown fox jumped over the lazy dog."
                )
            ]
        ),
        plan=[generate_words()],
    )


@solver
def generate_story_premise(
    premise: str = "[No requests, generate unique and engaging premises]",
):
    async def solve(state: TaskState, generate: Generate):
        msg_log = []
        msg = ChatMessageUser(
            role="user",
            content=prompts.prompt_gen_premises(
                n_clues=5, n_premises=1, user_request=premise
            ),
        )
        state.messages = [msg]
        await generate(state, cache=CachePolicy(expiry="12M"))
        msg_log.extend(state.messages)
        # [
        # {
        # "story_problem": "The story problem",
        # "hidden_clues": ["first hidden clue. Impact: the impact that it makes"],
        # "surprise_twist": "The surprise twist",
        # "ultimate_resolution": "The ultimate resolution"
        # }
        # ]
        output = state.output.completion
        if "```" in output:
            # trim everything before, AND everything afteron the same line as the ```
            splits = output.split("\n")
            start_index = 0
            for i in range(len(splits)):
                if "```" in splits[i]:
                    start_index = i + 1
                    break
            end_index = len(splits)
            for i in range(len(splits)):
                if "```" in splits[i]:
                    end_index = i - 1
                    break
            output = "\n".join(splits[start_index:end_index])

        print("output=", output)
        data = json.loads(output)
        # change selection if you want
        selected = data[0]
        msg = ChatMessageUser(
            role="user",
            content=prompts.prompt_gen_second_draft_premise(
                selected["story_problem"],
                selected["hidden_clues"],
                selected["surprise_twist"],
                selected["ultimate_resolution"],
            ),
        )
        print("output=", state.output.completion)
        state.messages = [msg]
        await generate(state, cache=CachePolicy(expiry="12M"))
        msg_log.extend(state.messages)

        state.messages = msg_log
        return state

    return solve


@task
def eval_gen_premise():
    return Task(
        dataset=MemoryDataset(
            [
                Sample(
                    input="none",
                )
            ]
        ),
        plan=[
            generate_story_premise(
                "Sexy and psychedelic science fiction that takes place on and around the moons of Jupiter. Main character is a 28 year old woman working in a bathhouse on a space station. Bath-house aesthetic is influenced by geisha culture. Intrigue is around mysterious alien sentience that is stretches our normal physical and human understanding of the universe."
            ),
        ],
    )
