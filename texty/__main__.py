from texty.models import vllm
from outlines import models, generate

# "Texty" is a text adventure program with a REPL
# you get to choose an adventure theme, or randomly generate one
# From there, the program will generate a story based on the theme
# While powered by a powerful LLM, gameplay is still restricted, and follows 
# common text adventure rules: 
# - predefined actinos
# - semi-predefined locations
# - inventory
def main():
    print("Welcome to Texty!")
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
    game_id = "game_1"  # Placeholder for game ID
    game_repl = GameREPL(game_id, state)
    game_loop(game_repl)

def load_game():
    print("Loading game... (This is a placeholder)")
    # Placeholder for loading game logic
    description = "Loaded game description"
    state = GameState(description=description)
    game_id = "game_1"  # Placeholder for game ID
    game_repl = GameREPL(game_id, state)
    game_loop(game_repl)

def game_loop(game_repl):
    while True:
        command = input("> ").strip()
        if command == "quit":
            print("Exiting game...")
            break
        else:
            response = game_repl.process_input(command)
            print(response)

if __name__ == "__main__":
    main()
