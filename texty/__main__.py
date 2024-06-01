from texty.game import run_game
    

if __name__ == "__main__":
    try:
        print("starting...")
        run_game()
    except KeyboardInterrupt:
        print("\nExiting game...")
