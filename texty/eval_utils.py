import json
from posixpath import dirname
from typing import Any, Callable, List, Literal

from inspect_ai.model import (
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageTool,
    ChatMessageUser,
)
from inspect_ai.solver import Generate, TaskState, solver


@solver
def render_prompt(
    promptfn: Callable[[TaskState], str],
    role: Literal["user", "assistant", "system", "tool"] = "user",
):
    async def solve(state: TaskState, generate: Generate):
        for message in state.messages[:]:
            if message.source == "input":
                state.messages.remove(message)
        prompt = promptfn(state)
        cls = (
            ChatMessageUser
            if role == "user"
            else (
                ChatMessageAssistant
                if role == "assistant"
                else ChatMessageSystem if role == "system" else ChatMessageTool
            )
        )
        msg = cls(role=role, content=prompt)
        state.messages.append(msg)
        return state

    return solve


def load_jsonl_data(path: str) -> List[Any]:
    with open(dirname(__file__) + "/../data" + path) as f:
        results = []
        for line in f:
            if line:
                results.append(json.loads(line))
        return results
