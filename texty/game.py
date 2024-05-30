import outlines.generate
import outlines.generate.text
from texty.gamestate import GameState

import outlines
from typing import Protocol, Any

from texty.io import IOInterface
from texty.models.vllm import get_chat_response
from texty.prompts import gen_game_state


class GameREPL:
    """
    Once a game is loaded, interface for controlling the game
    """

    state: GameState
    game_id: str
    io: IOInterface

    def __init__(self, game_id: str, state: GameState, io: IOInterface):
        self.io = io
        self.state = state
        self.game_id = game_id

    def initialize(self):
        """
        Initializes the world from the LLM, if not already initialized
        """
        if (
            self.state.environment == []
            or self.state.scenes == []
            or self.state.objectives == []
        ):
            prompt = gen_game_state(self.state.description)
            resp = get_chat_response(prompt)
            # TODO - Parse the response and update the game state
            pass
        

    def process_input(self, input: str) -> str:
        """Parses the raw user input into one of the available commands"""
        cmds = input.strip().split(" ", 2)
        cmd = cmds[0]
        if cmd == "/help":
            self.io.write_output(self.show_help())
        elif cmd == "/location":
            self.io.write_output(self.show_location(n=int(cmds[1]) if len(cmds) > 1 else 3))
        elif cmd == "/inventory":
            self.io.write_output(self.show_inventory())
        elif cmd == "/hint":
            self.io.write_output(self.show_actions(query=cmds[1] if len(cmds) > 1 else ""))
        elif cmd.startswith("/"):
            self.io.write_output(f"Unknown command '{cmd}'. Type /help for a list of commands, or otherwise type your input")
        else:
            self.io.write_output(self.take_action(input))

    def show_help(self) -> str:
        """/help - Command that prints a list of available commands"""
        return (
            "/help - Command that prints a list of available commands\n"
            "/location [n] - Command that prints information about the current location, and the past n locations\n"
            "/inventory - Command that prints information about the current inventory\n"
            "/hint [query] - Command that prints a hint about the currently available actions and objectives\n"
            "/text [message] - Command that sends a message to the LLM and gets a response\n"
            "/quit - Command that exits the game\n"
        )

    def show_location(self, n=3) -> str:
        """/location [n] - Command that prints information about the current location, and the past n locations"""
        pass

    def show_inventory(self) -> str:
        """/inventory - Command that prints information about the current inventory"""
        pass

    def show_actions(self, query: str) -> str:
        """/hint [query] - Command that prints a hint about the currently available actions and objectives"""
        pass

    def handle_text_command(self, text: str) -> str:
        """Handles the /text command"""
        # Implement the logic for the /text command here
        response = get_chat_response(text)
        return response

    def take_action(self, action: str) -> str:
        """/action [action] - Command that attempts to perform an action"""
        pass
