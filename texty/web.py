from dataclasses import dataclass, field
import datetime
import random
import uuid
import gradio as gr
from textwrap import dedent
from typing import Callable, Dict, Iterator, List, Optional, TypedDict
from texty import database, seeds
from texty.game import AdvanceTimeProgress, Game, StatusUpdate, TextResponse
from texty.gametypes import TimeNode


@dataclass
class Message:
    role: str
    content: str


@dataclass
class GameOutput:
    history: List[Message] = field(default_factory=list)
    inprogress: Optional[Message] = None
    event_log: Optional[str] = None

    def append_response_delta(self, role: str, response: str):
        if not self.inprogress:
            self.inprogress = Message(role=role, content="")
        self.inprogress.content += response

    def add_history(self, message: Message):
        assert message is not None
        self.inprogress = None
        self.history.append(message)

    def append_event_log_delta(self, event: str, debug: Optional[str] = None):
        if not self.event_log:
            self.event_log = ""
        self.event_log += event + (f"({debug})" if debug else "") + "\n"

    def get_text_log(self):
        messages = self.history[:]
        if self.inprogress:
            messages.append(self.inprogress)
        return "\n".join([f"{msg.role}:\n{msg.content}" for msg in messages])

    def get_response_tuples(self):
        current = [None, None]
        response = [current]
        messages = self.history[:]
        if self.inprogress:
            messages.append(self.inprogress)
        for msg in messages:
            if msg.role == "player":
                if current[0] is not None or current[1] is not None:
                    current = [None, None]
                    response.append(current)
                current[0] = msg.content
            elif msg.role == "game":
                if current[1] is not None:
                    current = [None, None]
                    response.append(current)
                current[1] = msg.content

        return response


class GradioInterface:
    def __init__(self):
        self.game = None
        self.game_output = GameOutput()

    def initialize_game(self, scenario_id: str, seed_name: str) -> Iterator[GameOutput]:
        database.init_db()
        self.game = Game(scenario_id=scenario_id)
        self.game_output = GameOutput()

        seed = getattr(seeds, seed_name, seeds.zantar)
        for event in self.game.start_if_not_started(seed=seed):
            if isinstance(event, StatusUpdate):
                self.game_output.append_event_log_delta(event.status, event.debug)
                yield self.game_output
            if isinstance(event, TextResponse):
                self.game_output.append_response_delta("game", event.delta)
                yield self.game_output
        if not self.game_output.inprogress:
            for event in self.game.node.event_log:
                if event.role != "internal":
                    self.game_output.add_history(
                        Message(role=event.role, content=event.text)
                    )
                    yield self.game_output
        else:
            self.game_output.add_history(self.game_output.inprogress)
        return self.game_output

    def delete_game(self):
        if self.game:
            database.delete_game(self.game.scenario_id)
        self.game = None

    def process_command(self, command: str) -> Iterator[GameOutput]:
        if not self.game:
            return "Error: Please initialize the game first."
        if not command:
            return

        if command.startswith("/"):
            self.handle_special_command(command)
            yield self.game_output
            return

        self.game_output.add_history(Message(role="player", content=command))
        self.game_output.append_response_delta("game", "")
        yield self.game_output
        for event in self.game.step(command):
            if isinstance(event, StatusUpdate):
                self.game_output.append_event_log_delta(event.status, event.debug)
                yield self.game_output
            if isinstance(event, TextResponse):
                self.game_output.append_response_delta("game", event.delta)
                yield self.game_output

        self.game_output.add_history(self.game_output.inprogress)
        return self.game_output

    def handle_special_command(self, command: str) -> str:
        if command == "/undo":
            message = "Can't go back. No parent node found"
            if self.game.undo():
                message = f"Loaded {self.game.node.id}: {self.game.node.summary}"
            self.game_output.add_history(Message(role="System", content=message))
        elif command == "/help":
            help_text = dedent(
                """
            Available commands:
            - /undo: Undo the last command
            - /help: Show this help message
            - <text>: Interact with the game by one timestep
            """
            ).strip()
            self.game_output.add_history(Message(role="System", content=help_text))
        else:
            self.game_output.add_history(
                Message(
                    role="System",
                    content=f"Unknown command: {command}. Type /help for a list of commands",
                )
            )


class ScenarioState(TypedDict):
    scenario_id: str
    seed: str


with gr.Blocks(title="Texty") as demo:
    database.init_db()
    gradio_game = GradioInterface()

    NONE = None

    scenario_id_state = gr.State(value=NONE)

    with gr.Row(visible=scenario_id_state.value != NONE) as game_row:

        def advance_game(command):
            yield {command_input: ""}
            for update in gradio_game.process_command(command):
                yield {syslog: update.event_log, chat: update.get_response_tuples()}

        with gr.Column():
            with gr.Row():
                with gr.Column():
                    chat = gr.Chatbot(
                        value=gradio_game.game_output.get_response_tuples(),
                        label="Texty",
                        layout="bubble",
                    )
                    # Add custom JavaScript to scroll the Chatbot to the bottom
                    js_code = dedent(
                        """
                        <script type="text/javascript">
                        function scrollToBottom() {
                            let chatbot = document.querySelector('.bubble-wrap');
                            console.log("hello world: ", chatbot);
                            if (chatbot) {
                                chatbot.scrollTop = chatbot.scrollHeight;
                            }
                        }
                        // Scroll to bottom after the interface loads
                        console.log("hiiiii");
                        window.addEventListener('load', scrollToBottom);
                        scrollToBottom();
                        </script>
                        """
                    ).strip()

                    # Add a hidden HTML component to include the JavaScript
                    gr.HTML(js_code)

                    command_input = gr.Textbox(
                        label="Enter Command",
                        placeholder="Type /help for list of options",
                    )
                    submit_button = gr.Button("Submit", variant="primary")
                syslog = gr.Textbox(
                    label="System Log",
                    lines=27,
                    scale=0,
                    min_width=300,
                    visible=True,
                    autoscroll=True,
                )
            with gr.Row():
                delete_button = gr.Button("Delete Game", variant="stop")
                quit_button = gr.Button("Leave Game")
                # scenario_id = gr.Textbox(label="Scenario ID")
                # seed_name = gr.Textbox(label="Seed Name", value="zantar")
                show_log = gr.Checkbox(label="Show Debug", value=True)
                # init_button = gr.Button("Initialize Game")

        def stream_updates_on_change(state: "ScenarioState"):
            if state != NONE:
                for update in gradio_game.initialize_game(
                    state["scenario_id"], state["seed"]
                ):
                    yield {syslog: update.event_log, chat: update.get_response_tuples()}

        scenario_id_state.change(
            stream_updates_on_change,
            inputs=[scenario_id_state],
            outputs=[chat, syslog],
        )

    with gr.Row(visible=scenario_id_state.value == NONE) as loader_row:
        with gr.Column():
            with gr.Row():
                gr.Markdown("# Texty")
                game_seeds = gr.Dropdown(
                    label="Game Seed",
                    choices=["zantar", "lost_expedition"],
                    value="zantar",
                    multiselect=False,
                )
                new_game_button = gr.Button("New Game", variant="primary")
            games = gr.State(None)

            def transform_rows(
                rows: Optional[List[tuple[datetime.datetime, TimeNode]]]
            ):
                if not rows:
                    return []
                else:
                    return [
                        [row[0], row[1].timestep, row[1].summary, row[1].id]
                        for row in rows
                    ]

            game_table = gr.DataFrame(
                [],
                headers=["Last Updated", "Timestep", "Summary", "ID"],
                interactive=False,
                visible=True,
            )
            games.change(transform_rows, inputs=games, outputs=game_table)

            def load_games(scenario_id: Optional[ScenarioState]):
                if not scenario_id:
                    return database.list_games()  # , gr.update(visible=True)
                else:
                    return None

            demo.load(load_games, inputs=scenario_id_state, outputs=[games])
            scenario_id_state.change(
                load_games, inputs=scenario_id_state, outputs=[games]
            )

            def select_game(games, evt: gr.SelectData, seed: str):
                game = games[evt.index[0]]
                scenario_id = game[1].scenario_id()
                return {
                    scenario_id_state: ScenarioState(scenario_id=scenario_id, seed=seed)
                }

            def new_game(seed):
                if not seed:
                    return
                id = str(uuid.uuid4())
                return {
                    scenario_id_state: ScenarioState(scenario_id=id, seed=seed),
                }

            game_table.select(
                select_game, inputs=[games, game_seeds], outputs=scenario_id_state
            )
            new_game_button.click(
                new_game,
                inputs=[game_seeds],
                outputs=[scenario_id_state],
            )

    def toggle_views_on_state_change(node_id: str, seed: str):
        return {
            game_row: gr.update(visible=node_id != NONE),
            loader_row: gr.update(visible=node_id == NONE),
        }

    scenario_id_state.change(
        toggle_views_on_state_change,
        inputs=[scenario_id_state, game_seeds],
        outputs=[game_row, loader_row],
    )

    def on_quit():
        return NONE

    def on_delete():
        gradio_game.delete_game()
        return NONE

    quit_button.click(on_quit, outputs=[scenario_id_state])
    delete_button.click(on_delete, outputs=[scenario_id_state])

    def toggle_log(show_log):
        return gr.update(visible=show_log)

    show_log.change(fn=toggle_log, inputs=show_log, outputs=syslog)

    submit_button.click(
        fn=advance_game,
        inputs=command_input,
        outputs=[syslog, chat, command_input],
    )

    command_input.submit(
        fn=advance_game,
        inputs=command_input,
        outputs=[syslog, chat, command_input],
    )

if __name__ == "__main__":

    demo.launch()
