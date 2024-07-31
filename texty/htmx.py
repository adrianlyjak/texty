from textwrap import dedent
from typing import AsyncGenerator
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from fasthtml.common import *
import starlette
import starlette.requests
import os
from texty import database, seeds
from texty import game
from texty.gametypes import LogItem, TimeNode
import jinja2

app = FastHTMLWithLiveReload()
rt = app.route


def partial(path: str) -> str:
    with open(os.path.join("www", "partial", path), "r") as f:
        return f.read()


LOGO = """<svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,10 85,30 85,70 50,90 15,70 15,30" stroke="black" stroke-width="2" fill="white"/>
</svg>
"""


def navbar(extra_cls: str = "", sticky: bool = True) -> Nav:
    return NotStr(
        f"""
<header class="{extra_cls} {'sticky-top' if sticky else ''} navbar bg-body">
    <nav class="header container">
        <div class="logo-container"><a href="/" class="logo-link">{LOGO}</a></div>
        <h1>RNGes.us</h1>
    </nav>
</header>
"""
    )


def page(*children):
    corehtml = partial("core.html")
    return (
        Title("RNG"),
        NotStr(corehtml),
        navbar(),
        Main(*children, cls="container"),
    )


@rt("/")
def get(request: starlette.requests.Request):

    blurcss = partial("css/splash-header.css")
    corehtml = partial("core.html")

    return page(
        Title("RNG"),
        NotStr(corehtml),
        Main(Style(blurcss), NotStr(partial("homepage.html")), cls="container"),
    )


@rt("/join")
def get():
    return Div("Clicked it!")


@rt("/games")
def get():

    games = database.list_games()

    saved_games = []
    for timestamp, game in games:
        time_fmt = timestamp.strftime("%Y-%m-%d %H:%m:%S %p")
        saved_games.append(
            A(
                Div(
                    f"{time_fmt} - {game.summary}",
                ),
                href="/game/" + game.scenario_id(),
            )
        )
    return page(
        H2("Load Game"),
        *saved_games,
    )


@rt("/games/create")
def get():
    new_story_form = jinja2.Template(partial("new-story-form.jinja"))
    options = [
        {"id": seed, "summary": f"{seed}: {seeds.get_seed(seed).premise}"}
        for seed in seeds.list_seeds()
    ]
    form = new_story_form.render(options=options)
    return page(NotStr(form))


@dataclass
class CreateGameRequest:
    prompt: Optional[str] = None
    template: Optional[str] = None


@rt("/games/create")
async def post(data: CreateGameRequest):

    # return HTMLResponse(headers={"HX-Redirect": "/" })
    if data.prompt:
        seed: TimeNode = await game.Game.from_prompt(data.prompt)
        return HTMLResponse(headers={"HX-Redirect": "/game/" + seed.scenario_id()})
    elif data.template:
        seed = game.Game.from_seed(data.template)
        return HTMLResponse(headers={"HX-Redirect": "/game/" + seed.scenario_id()})
    else:
        return Div(
            Div("Select a template or enter a prompt", cls="card bg-error"),
            id="form-alerts",
        )


@rt("/game/{scenario_id}")
def get(scenario_id: str):

    input = to_xml(game_input_area())
    main = jinja2.Template(partial("empty-game.jinja")).render(
        scenario_id=scenario_id, game_input_area=input
    )
    corehtml = partial("core.html")

    return (Title("RNG"), NotStr(corehtml), navbar(sticky=False), NotStr(main))


def game_input_area() -> Div:
    return Div(
        Textarea(
            id="game-input",
            name="game-input",
            placeholder="Enter an action",
            onInput="this.parentNode.dataset.replicatedValue = this.value",
            cls="mb-0 form-control border-1 border-primary",
        ),
        cls="grow-wrap",
        id="game-input-area",
    )


@dataclass
class Message:
    role: str
    content: str


def game_message(role: str, content: str, id: Optional[str] = None) -> Div:
    lines = content.split("\n")
    nodes = []
    for i, line in enumerate(lines):
        nodes.append(line)
        if i < len(lines) - 1:
            nodes.append(Br())
    return Div(*nodes, cls=f"game-message-{role}", id=id)


def icon(type: str) -> I:
    return I(Script("lucide.createIcons();"), data_lucide=type)


async def websocket_handler(socket: WebSocket):
    scenario_id = socket.url.path.removeprefix("/ws/scenario/")

    async def send_msg(role: str, msg: str, id: Optional[str] = None) -> None:
        """Adds a single message with the specified role and content to the chat history"""
        await socket.send_text(
            to_xml(
                Div(
                    game_message(role, msg, id=id),
                    id="game-content",
                    hx_swap_oob="beforeend",
                )
            )
        )

    async def set_messages(items: List[LogItem]):
        """Sets the full list of messages to these log items"""
        children = [game_message(msg.role, msg.text) for msg in items]
        await socket.send_text(to_xml(Div(*children, id="game-content")))

    def split_with_line_breaks(content: str) -> List[Union[str, Br]]:
        nodes = []
        parts = content.split("\n")
        for i, msg in enumerate(parts):
            nodes.append(msg)
            if i < len(parts) - 1:
                nodes.append(Br())
        return nodes

    async def stream_msg(
        role: str, generator: AsyncGenerator[game.AdvanceTimeProgress, None]
    ) -> None:
        """streams an in progress message from a game interaction. Shows progress indicators and adds an intermediary system messages"""
        id = "msg-" + str(uuid.uuid4())
        # prepare elements for updates
        await send_msg("system", "", id=f"{id}-system")
        await send_msg(role, "", id=id)
        await socket.send_text(
            to_xml(Div(Div(id=f"{id}-progress"), id=id, hx_swap_oob="afterstart"))
        )
        buff = ""
        async for msg in generator:
            match msg:
                case game.TextResponse():
                    # if naively forwarding messages on to htmx, it adds a new line, so tokens for partial words end up getting spaces injected between them.
                    # So only send update messages that are divided by spaces
                    buff += msg.delta
                    last_index = buff.rindex(" ") if " " in buff else 0
                    to_send = buff[:last_index]
                    buff = buff[last_index:]
                    nodes = split_with_line_breaks(to_send)
                    await socket.send_text(
                        to_xml(Div(*nodes, id=id, hx_swap_oob="beforeend"))
                    )
                case game.DiceRoll():
                    percent = f"{(msg.chance_success * 100):.2f}".rstrip("0").rstrip(
                        "."
                    )
                    content = []
                    if msg.did_succeed == True:
                        content = [
                            f"{percent}% chance of success",
                            Div("succeeded!", cls="tag is-small bg-success"),
                        ]
                    elif msg.did_succeed == False:
                        content = [
                            f"{percent}% chance of success",
                            Div("failed!", cls="tag is-small bg-error"),
                        ]
                    else:
                        content = [
                            f"{percent}% chance of success",
                            Div("...", cls="tag is-small bg-warning"),
                        ]
                    await socket.send_text(
                        to_xml(
                            Div(
                                Div(icon("dices"), *content),
                                id=f"{id}-system",
                                cls="game-message-system",
                            )
                        )
                    )
                case game.TimeNodeUpdate():
                    pass
                case game.ProgressUpdate():
                    if msg.progress == 0:
                        await socket.send_text(
                            to_xml(
                                Div(
                                    Div(
                                        f"{msg.type}: {msg.progress}",
                                        id=f"{id}-progress-{msg.type}",
                                    ),
                                    id=f"{id}-progress",
                                    hx_swap_oob="beforeend",
                                )
                            )
                        )
                    else:
                        await socket.send_text(
                            to_xml(
                                Div(
                                    f"{msg.type}: {msg.progress}",
                                    id=f"{id}-progress-{msg.type}",
                                )
                            )
                        )

        if buff:
            nodes = split_with_line_breaks(buff)
            await socket.send_text(to_xml(Div(*nodes, id=id, hx_swap_oob="beforeend")))
        socket.send_text(to_xml(Div(id=f"{id}-progress")))

    try:
        await socket.accept()
        scenario = game.Game(scenario_id=scenario_id)

        await stream_msg("game", scenario.start_if_not_started_async())
        await set_messages(
            [evt for evt in scenario.node.event_log if evt.role != "internal"]
        )

        while True:
            message = await socket.receive_json()
            txt = message.get("game-input", "").strip()
            await send_msg("player", txt)
            await socket.send_text(to_xml(game_input_area()))
            if txt == "/undo":
                if scenario.undo():
                    await set_messages(
                        [
                            evt
                            for evt in scenario.node.event_log
                            if evt.role != "internal"
                        ]
                    )
                    await send_msg("system", "Undo successful")
                else:
                    await send_msg("system", "Undo failed")
            elif txt:

                await stream_msg("game", scenario.step_async(txt))

    except WebSocketDisconnect as e:
        pass


app.add_websocket_route("/ws/scenario/{scenario_id}", websocket_handler)

app.routes.append(
    Mount("/static", app=StaticFiles(directory="www/static"), name="static"),
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
