import os
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import generate
from texty.prompts import activate_game_state, gen_world, gen_world_objective
from texty.gamestate import GameState
from texty.eval_utils import load_jsonl_data, render_prompt


labyrinth = Sample(
    input="A puzzle game set in a labyrinth, where you must use your wits to find your way out."
)
future_detective = Sample(
    input="A detective game set in a futuristic city, where you must solve a series of murders.",
    metadata={
        "world": load_jsonl_data("/tests/future_detective/world.jsonl"),
        "objectives": load_jsonl_data("/tests/future_detective/objectives.jsonl"),
    },
)


@task()
def eval_gen_world_puzzle():
    return Task(
        dataset=MemoryDataset(
            samples=[labyrinth, future_detective],
        ),
        plan=[
            render_prompt(lambda s: gen_world(s.input)),
            generate(),
        ],
    )


@task()
def eval_objectives():
    return Task(
        dataset=MemoryDataset(
            samples=[future_detective],
        ),
        plan=[
            render_prompt(lambda s: gen_world_objective(s.input, s.metadata["world"])),
            generate(),
        ],
    )


@task()
def eval_intro_scene():
    return Task(
        dataset=MemoryDataset(
            samples=[future_detective],
        ),
        plan=[
            render_prompt(
                lambda s: activate_game_state(
                    GameState(
                        description=s.input,
                        environment=s.metadata["world"],
                        objectives=s.metadata["objectives"],
                    )
                )
            ),
            generate(),
        ],
    )


@task()
def eval_activate_game_state():
    return Task(
        dataset=MemoryDataset(
            samples=[future_detective],
        ),
        plan=[
            render_prompt(
                lambda s: activate_game_state(
                    GameState(
                        description=s.input,
                        environment=s.metadata["world"],
                        objectives=s.metadata["objectives"],
                    )
                )
            ),
            generate(),
        ],
    )


@task()
def eval_prewrite_new_activated_game_state():
    return Task(
        dataset=MemoryDataset(
            samples=[future_detective],
        ),
        plan=[
            render_prompt(
                lambda s: activate_game_state(
                    GameState(
                        description=s.input,
                        environment=s.metadata["world"],
                        objectives=s.metadata["objectives"],
                    )
                )
            ),
            generate(),
        ],
    )
