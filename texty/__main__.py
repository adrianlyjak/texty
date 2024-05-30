import uuid
from texty import database
from texty.gamestate import GameState
from texty.game import GameREPL, IOInterface
from texty.io import StdIOInterface


# "Texty" is a text adventure program with a REPL
# you get to choose an adventure theme, or randomly generate one
# From there, the program will generate a story based on the theme
# While powered by a powerful LLM, gameplay is still restricted, and follows
# common text adventure rules:
# - predefined actions
# - semi-predefined locations
# - inventory
def main():
    io = StdIOInterface()
    io.write_output("Welcome to Texty!")
    database.initialize_db()
    while True:
        io.write_output(
            (
                """Main Menu:
1. New Game
2. Load Game
3. Quit"""
            )
        )
        choice = io.read_input("Choose an option: ").strip()

        if choice == "1":
            new_game(io)
        elif choice == "2":
            load_game(io)
        elif choice == "3":
            io.write_output("Thanks for playing!")
            break
        else:
            io.write_output("Invalid choice. Please select 1, 2, or 3.")


def new_game(io: IOInterface):
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
    main()
