import re
from textwrap import dedent
import uuid
from texty import database
from texty.gamestate import GameRow, GameState

from typing import List, Optional, Any

from texty.io import IOInterface, Panel, RichInterface, list_choice
from texty.models.vllm import get_chat_response, stream_chat_response
from texty.prompts import gen_world, gen_concepts
from rich.markdown import Markdown


def run_game():
    io = RichInterface()
    database.initialize_db()
    io.write_output(
        dedent(
            """
            *-------------------*
            | [bold cyan]Welcome to Texty![/bold cyan] |
            *-------------------*
            """
        ).strip()
    )
    game = database.last_game()
    if game:
        resume_game(io, game)    
    else:
        new_game(io)

def resume_game(io: IOInterface, game: GameRow):
    state = GameState.model_validate_json(game.state)
    game_repl = GameREPL(game.id, state, io)
    game_loop(game_repl)


def main_menu(io: IOInterface):
    choices = ["New Game", "Load Game", "Quit"]
    while True:
        choice = list_choice(io, "Choose an option: ", choices)
        if choice == 1:
            new_game(io)
        elif choice == 2:
            load_game(io)
        elif choice == 3:
            io.write_output("Thanks for playing!")
            break


def as_bullet(x: str) -> Optional[str]:
    if re.match("^- ", x.strip()):
        return re.sub("^\s*- ", "", x)
    return None


def fetch_options(io: IOInterface, initial=[], n=3, hint: Optional[str] = None) -> List[str]:
    options = []

    # add numbers
    def log_options(items: List[str], panel: Panel):
        panel.update(
                Markdown(
                    "\n".join(
                        [
                            str(i + 1 + len(initial)) + ". " + item
                            for i, item in enumerate(items)
                        ]
                    ) + "\n\n"
                )
            )
    with io.live_panel("Generating ideas...") as panel:
        current = ""
        for x in stream_chat_response(gen_concepts(n=n, hint=hint, previous=initial)):
            parts = x.split("\n")
            current += parts[0]
            if len(parts) > 1:
                candidates = [current] + parts[1:-1]
                for c in candidates:
                    bullet = as_bullet(c)
                    if bullet:
                        options.append(bullet)
                current = parts[-1]
            
            log_options(options + ([as_bullet(current)] if as_bullet(current) else []), panel)
        if current and as_bullet(current):
            options.append(as_bullet(current))
            log_options(options, panel)
    return options

def new_game(io: IOInterface):
    options = []
    selection = None
    hint = None
    while selection is None:
        options.extend(fetch_options(io, initial=options, hint=hint))
        hint = None
        selection_str = io.read_input("Pick a number, or 'm' for more, or give a hint as to the kind of game you would like: ").strip()
        if selection_str == "m":
            continue
        if not selection_str.isdigit():
            hint = selection_str
            continue
        selection_idx = int(selection_str) - 1
        if selection_idx < 0 or selection_idx >= len(options):
            io.write_output("Invalid choice. Please select a valid option.")
            continue

        selection = options[selection_idx]
    state = GameState(description=selection)
    game_id = str(uuid.uuid4())  # Generate a new random UUID for game ID
    game_repl = GameREPL(game_id, state, io)
    database.save_game_state(game_id, state)
    game_loop(game_repl)


def load_game(io: IOInterface):
    games = database.list_games()
    games.sort(key=lambda x: x.updated, reverse=True)
    if not games:
        io.write_output("No saved games found.")
        return

    io.write_output("Saved games:")
    for idx, game in enumerate(games, start=1):
        gs = GameState.model_validate_json(game.state)
        io.write_output(f"{idx}. {gs.description} (Last updated: {game.updated})")

    choice = input("Enter the number of the game you want to load: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(games):
        io.write_output("Invalid choice.")
        return

    game = games[int(choice) - 1]
    resume_game(io, game)

def game_loop(game_repl: "GameREPL"):
    game_repl.initialize()
    while True:
        command = game_repl.io.read_input("> ").strip()
        if command == "/quit":
            game_repl.io.write_output("Exiting game...")
            break
        else:
            game_repl.process_input(command)


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
            with self.io.live_panel("Generating game state...") as panel:
                prompt = gen_world(self.state.description)
                resp = get_chat_response(prompt)
                # TODO - Parse the response and update the game state
                pass

    def process_input(self, input: str) -> None:
        """Parses the raw user input into one of the available commands"""
        cmds = input.strip().split(" ", 2)
        cmd = cmds[0]
        if cmd == "/help":
            self.io.write_output(self.show_help())
        elif cmd == "/location":
            self.show_location(n=int(cmds[1]) if len(cmds) > 1 else 3)
        elif cmd == "/inventory":
            self.show_inventory()
        elif cmd == "/hint":
            self.show_actions(query=cmds[1] if len(cmds) > 1 else "")
        elif cmd.startswith("/"):
            self.io.write_output(
                f"Unknown command '{cmd}'. Type /help for a list of commands, or otherwise type your input"
            )
        else:
            self.take_action(input)

    def show_help(self) -> str:
        """/help - Command that prints a list of available commands"""
        self.io.write_output(
            "/help - Command that prints a list of available commands\n"
            "/location [n] - Command that prints information about the current location, and the past n locations\n"
            "/inventory - Command that prints information about the current inventory\n"
            "/hint [query] - Command that prints a hint about the currently available actions and objectives\n"
            "/text [message] - Command that sends a message to the LLM and gets a response\n"
            "/quit - Command that exits the game\n"
        )

    def show_location(self, n=3) -> str:
        """/location [n] - Command that prints information about the current location, and the past n locations"""
        if not self.state.navigation_history:
            self.io.write_output("No navigation history available.")
            return

        history = self.state.navigation_history[-n:]
        scenes_dict = {scene.id: scene for scene in self.state.scenes}
        location_details = []

        for scene_id in history:
            scene = scenes_dict.get(scene_id)
            if scene:
                details = (
                    f"Scene ID: {scene.id}\n"
                    f"Description: {scene.description}\n"
                    f"Actions: {', '.join(scene.actions)}\n"
                    f"Items: {', '.join(scene.items)}\n"
                    f"Exits: {', '.join(scene.exits)}"
                )
                location_details.append(details)

        self.io.write_output(
            "Current location and past {} locations:\n\n{}".format(
                n, "\n\n".join(location_details)
            )
        )

    def show_inventory(self) -> str:
        """/inventory - Command that prints information about the current inventory"""
        if not self.state.inventory:
            self.io.write_output("Your inventory is empty.")
        else:
            inventory_list = "\n".join(f"- {item}" for item in self.state.inventory)
            self.io.write_output(f"Current inventory:\n{inventory_list}")

    def show_actions(self, query: str) -> str:
        """/hint [query] - Command that prints a hint about the currently available actions and objectives"""
        self.io.write_output(
            "Hint about the currently available actions and objectives."
        )

    def handle_text_command(self, text: str) -> str:
        """Handles the /text command"""
        # Implement the logic for the /text command here
        response = get_chat_response(text)
        return response

    def take_action(self, action: str) -> str:
        """/action [action] - Command that attempts to perform an action"""
        self.io.write_output("Attempting to perform action: {}".format(action))
