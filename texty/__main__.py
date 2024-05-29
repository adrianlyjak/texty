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
    # Initialize the game state.
    # Starts with a main menu: offering options: new, load, quit
    # 
    # Screen New:
    #  user writes out a scenario, then game initializes its state from the scenario. Proceeds to gameplay
    #     - future enhancements: generate potential scenarios (with or without user input)
    # Screen Load:
    #     - selectable list of all previous scenarios (games are autosaved)
    #     - on enter, proceeds to gameplay
    # Gameplay:
    #     - See game.py

    
    # TODO - entirely rewrite this commented section to follow above
    pass
    # current_location = "start"
    # locations = {
    #     "start": "You are in a small room with a door to the north.",
    #     "north_room": "You are in a beautiful garden. There is a path to the south."
    # }
    
    # print("Welcome to the tiny adventure!")
    # print(locations[current_location])
    
    # # Main game loop
    # while True:
    #     command = input("> ").strip().lower()  # Read input from the user
        
    #     if command == "quit":
    #         print("Thanks for playing!")
    #         break
    #     elif command == "look":
    #         print(locations[current_location])
    #     elif command == "go north" and current_location == "start":
    #         current_location = "north_room"
    #         print(locations[current_location])
    #     elif command == "go south" and current_location == "north_room":
    #         current_location = "start"
    #         print(locations[current_location])
    #     else:
    #         print("I don't understand that command.")

if __name__ == "__main__":
    main()
