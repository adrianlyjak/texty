import dataclasses
from typing import TypedDict, Literal, List

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class PrewritingState(TypedDict):
    objectives: List[str]
    environment: List[str]

class GameState(TypedDict):
    description: str
    log: List[Message]