from textwrap import dedent
import uuid
from texty import database
from texty.gamestate import GameState
from texty.game import GameREPL, IOInterface
from texty.io import RichInterface, StdIOInterface, list_choice
from texty.models.vllm import stream_chat_response
from texty.prompts import gen_introduction_system


# "Texty" is a text adventure program with a REPL
# you get to choose an adventure theme, or randomly generate one
# From there, the program will generate a story based on the theme
# While powered by a powerful LLM, gameplay is still restricted, and follows
# common text adventure rules:
# - predefined actions
# - semi-predefined locations
# - inventory
def main():
    io = RichInterface()
    database.initialize_db()
    io.write_output(
        dedent(
            """
            *-------------------*
            | Welcome to Texty! |
            *-------------------*
            """
        ).strip()
    )
    main_menu(io)


def main_menu(io: IOInterface):
    database.initialize_db()
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


def new_game(io: IOInterface):
    for x in stream_chat_response(gen_introduction_system()):
        io.write_output(x, end="")
    io.write_output("")
    description = io.read_input("Enter a description for your new game: ").strip()
    state = GameState(description=description)
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

    print("Available games:")
    for idx, game in enumerate(games, start=1):
        gs = GameState.model_validate_json(game.state)
        io.write_output(f"{idx}. {gs.description} (Last updated: {game.updated})")

    choice = input("Enter the number of the game you want to load: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(games):
        io.write_output("Invalid choice.")
        return

    game = games[int(choice) - 1]
    state = GameState.model_validate_json(game.state)

    game_repl = GameREPL(game.id, state, io)
    game_loop(game_repl)


def game_loop(game_repl: GameREPL):
    game_repl.initialize()
    while True:
        command = game_repl.io.read_input("> ").strip()
        if command == "/quit":
            game_repl.io.write_output("Exiting game...")
            break
        else:
            game_repl.process_input(command)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting game...")
