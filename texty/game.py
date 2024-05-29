

from texty.gamestate import GameState


class GameREPL():
    """
    Once a game is loaded, interface for controlling the game
    """
    state: GameState
    game_id: str

    def __init__(self, game_id: str, state: GameState):
        self.state = state
        self.game_id = game_id

    def process_input(self, input: str) -> str:
        """Parses the raw user input into one of the available commands"""
        cmds = input.strip().split(" ", 2)
        cmd = cmds[0]
        if cmd == "/help":
            return self.show_help()
        elif cmd == "/location":
            return self.show_location(n=int(cmds[1]) if len(cmds) > 1 else 3)
        elif cmd == "/inventory":
            return self.show_inventory()
        elif cmd == "/hint":
            return self.show_actions(query=cmds[1])
        elif cmd == "/take":
            return self.take_action(action=cmds[1])
        else:
            return f"Unknown command '{cmd}'. Type /help for a list of commands"

    def show_help(self) -> str:
        """/help - Command that prints a list of available commands"""
        pass

    def show_location(self, n=3) -> str:
        """/location [n] - Command that prints information about the current location, and the past n locations"""
        pass

    def show_inventory(self) -> str:
        """/inventory - Command that prints information about the current inventory"""
        pass

    def show_actions(self, query: str) -> str:
        """/hint [query] - Command that prints a hint about the currently available actions and objectives"""
        pass

    def take_action(self, action: str) -> str:
        """/action [action] - Command that attempts to perform an action"""
        pass