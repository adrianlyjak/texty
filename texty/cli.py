from textwrap import dedent
from typing import Iterator, Optional
from texty import database, seeds
from texty.game import AdvanceTimeProgress, Game, StatusUpdate, TextResponse
from texty.gametypes import TimeNode
from texty.io import RichInterface


def run_scenario(scenario_id: str, seed: TimeNode = seeds.zantar) -> TimeNode:

    database.init_db()
    game = Game(scenario_id=scenario_id)
    io = RichInterface()

    def print_game_response(
        iterator: Iterator[AdvanceTimeProgress], if_empty: Optional[str] = None
    ) -> None:
        status = ""
        with io.live_panel("") as panel:
            txt = ""
            any = False
            for event in iterator:
                any = True
                if type(event) == StatusUpdate:
                    status = event.status + (f" ({event.debug})" if event.debug else "")
                    panel.update(status + "\n" + txt)
                elif type(event) == TextResponse:
                    txt = event.full_text
                    panel.update(status + "\n" + txt)
            if not any and if_empty:
                panel.update(if_empty)

    print_game_response(game.start_if_not_started(seed=seed), if_empty="Loaded game. Run '/history' to see the game history")

    try:
        while True:
            action = io.read_input("> ")
            if action == "/quit":
                break
            elif action == "/undo":
                loaded = game.undo()
                if not loaded:
                    io.write_output("Can't go back. No parent node found")
                else:
                    io.write_output("Loaded " + game.node.id + ": " + game.node.summary)
            elif action.startswith("/history"):
                io.write_output("## Game history")
                maxlen = 400
                parts = action.split(" ")
                if len(parts) > 1:
                    maxlen = int(parts[1])
                for event_log in game.node.event_log:
                    prefix = f"> {event_log.role}({event_log.type}): "
                    start = int(maxlen / 2 - 5)
                    end = int((-1 * maxlen / 2))
                    trunc = (
                        event_log.text[:start] + " ... " + event_log.text[end:]
                        if len(event_log.text) > maxlen
                        else event_log.text
                    )
                    print(prefix + trunc)
            elif action == "/help":
                io.write_output(
                    dedent(
                        """
                        Available commands:
                        - /quit: Exit the game
                        - /undo: Undo the last command
                        - /help: Show this help message
                        - /history: Show the game's history
                        - <text>: Interact with the game by one timestep"""
                    ).strip()
                )
            elif action.startswith("/"):
                io.write_output(
                    "Unknown command: " + action + ". Type /help for a list of commands"
                )
            elif not action.strip():
                pass
            else:
                print_game_response(game.step(action))
    except KeyboardInterrupt:
        io.write_output("Exiting...")
