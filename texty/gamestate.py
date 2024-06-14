from pydantic import BaseModel
from typing import List


# class GameIdeation(BaseModel):
#     recommendation: Optional[str]
#     results: Optional[List[str]]


class GameRow(BaseModel):
    id: str
    state: str
    created: str
    updated: str


class GameState(BaseModel):
    """
    All the game state
    """

    # The initial description of the game
    description: str
    # model defined game objectives
    objectives: List[str] = []
    # model defined world building
    environment: List[str] = []
    # objectives that have become active to the game
    current_objectives: List[str] = []
    # environment details that have become active
    current_environment: List[str] = []
    # model defined "rooms"
    scenes: List["Scene"] = []
    # past rooms visited, from first to last
    navigation_history: List[str] = []
    # past actions taken, from first to last
    action_history: List[str] = []
    # Øitems in the inventory
    inventory: List[str] = []


class Scene(BaseModel):
    id: str
    description: str
    actions: List[str] = []
    items: List[str] = []
    exits: List[str] = []
