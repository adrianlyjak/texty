import uuid
from texty.database import initialize_db, list_game_ids, load_game_state
from texty.models import vllm
from outlines import models, generate
from texty.gamestate import GameState
from texty.game import GameREPL

# "Texty" is a text adventure program with a REPL
# you get to choose an adventure theme, or randomly generate one
# From there, the program will generate a story based on the theme
# While powered by a powerful LLM, gameplay is still restricted, and follows 
# common text adventure rules: 
# - predefined actions
# - semi-predefined locations
# - inventory
def main():
    print("Welcome to Texty!")
    initialize_db()
    while True:
        print("\nMain Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_game()
        elif choice == "2":
            load_game()
        elif choice == "3":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def new_game():
    description = input("Enter a description for your new game: ").strip()
    state = GameState(description=description)
    game_id = str(uuid.uuid4())  # Generate a new random UUID for game ID
    game_repl = GameREPL(game_id, state)
    game_loop(game_repl)

def load_game():
    game_ids = list_game_ids()
    if not game_ids:
        print("No saved games found.")
        return

    print("Available games:")
    for idx, gid in enumerate(game_ids, start=1):
        print(f"{idx}. {gid}")

    choice = input("Enter the number of the game you want to load: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(game_ids):
        print("Invalid choice.")
        return

    game_id = game_ids[int(choice) - 1]
    state = load_game_state(game_id)
    if state is None:
        print("Failed to load the game state.")
        return

    game_repl = GameREPL(game_id, GameState(**state))
    game_loop(game_repl)

def game_loop(game_repl: GameREPL):
    while True:
        command = input("> ").strip()
        if command == "/quit":
            print("Exiting game...")
            break
        else:
            response = game_repl.process_input(command)
            print(response)

if __name__ == "__main__":
    main()
