import uuid
from texty import database
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
    database.initialize_db()
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
        elif command.startswith("/text "):
            text = command[len("/text "):]
            print(game_repl.handle_text_command(text))
            print("Invalid choice. Please select 1, 2, or 3.")

def new_game():
    description = input("Enter a description for your new game: ").strip()
    state = GameState(description=description)
    game_id = str(uuid.uuid4())  # Generate a new random UUID for game ID
    game_repl = GameREPL(game_id, state)
    database.save_game_state(game_id, state)
    game_loop(game_repl)

def load_game():
    games = database.list_games()
    games.sort(key=lambda x: x.updated, reverse=True)
    if not games:
        print("No saved games found.")
        return

    print("Available games:")
    for idx, game in enumerate(games, start=1):
        gs = GameState.model_validate_json(game.state)
        print(f"{idx}. {gs.description} (Last updated: {game.updated})")

    choice = input("Enter the number of the game you want to load: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(games):
        print("Invalid choice.")
        return

    game = games[int(choice) - 1]
    state = GameState.model_validate_json(game.state)

    game_repl = GameREPL(game.id, state)
    game_loop(game_repl)

def game_loop(game_repl: GameREPL):
    game_repl.initialize()
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
