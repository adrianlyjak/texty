import logging
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import Generate, TaskState, call_tools, generate, solver
from inspect_ai.model import ChatMessageUser
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
        state = await generate(state, cache=True)
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
            generate(cache=True),
        ],
    )


from typing import List, Literal
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
