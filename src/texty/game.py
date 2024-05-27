import dataclasses
from typing import TypedDict, Literal, List

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class InternalState(TypedDict):
    """
    Internal state and prewriting of the language models story objectives
    """
    objectives: List[str]
    environment: List[str]

class GameState(TypedDict):
    """
    All the game state
    """
    description: str
    log: List[Message]
    internal: InternalState


class GameProtocol():
    state: GameState
    
    def get_inventory() -> List[str]:
        pass

    def put_action(action: str) -> Message:
        pass

    def get_valid_actions() -> List[str]:
        pass
    
    def get_location() -> str:
        pass

