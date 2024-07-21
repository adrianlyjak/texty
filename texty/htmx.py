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

app = FastHTMLWithLiveReload()
rt = app.route


def partial(path: str) -> str:
    with open(os.path.join("www", "partial", path), "r") as f:
        return f.read()


LOGO = """<svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,10 85,30 85,70 50,90 15,70 15,30" stroke="black" stroke-width="2" fill="white"/>
</svg>
"""


def navbar() -> Nav:
    return Nav(
        Div(
            A(
                NotStr(LOGO),
                href="/",
                cls="logo-link",
            ),
            cls="logo-container",
        ),
        H1("RNGes.us"),
        cls="header",
    )


def page(*children):
    corehtml = partial("core.html")
    return (
        Title("RNG"),
        NotStr(corehtml),
        Div(navbar(), *children, cls="container"),
    )


@rt("/")
def get(request: starlette.requests.Request):

    blurcss = partial("css/splash-header.css")

    games = database.list_games()

    return page(
        Style(blurcss),
        Main(
            Div(
                Img(src="static/img/rngesus13.jpg"),
                cls="header-hero-img col",
            ),
            Div(
                A(
                    "Load Game",
                    href="/games",
                    name="load-game",
                ),
                A(
                    "New Game",
                    href="/games/create",
                    name="new-game",
                    cls="button primary",
                ),
                cls="col button-container",
            ),
            cls="row reverse",
        ),
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
        Main(
            H2("Load Game"),
            *saved_games,
        ),
    )


@rt("/games/create")
def get():
    corehtml = partial("core.html")
    all_seeds = [(seed, seeds.get_seed(seed)) for seed in seeds.list_seeds()]
    return (
        Title("RNG"),
        NotStr(corehtml),
        Main(
            navbar(),
            Section(id="form-alerts"),
            Section(
                H4("Select a Template"),
                Form(
                    Label("Template", name="template"),
                    Select(
                        *[
                            Option(seed_name + ": " + seed.premise, value=seed_name)
                            for seed_name, seed in all_seeds
                        ],
                        name="template",
                    ),
                    Button("Start", cls="send-button button primary", type="submit"),
                    hx_post="/games/create",
                ),
            ),
            Section(
                H4("Or Create Your Own"),
                Form(
                    Textarea(
                        name="prompt",
                        placeholder="Describe the game",
                    ),
                    Button("Start", cls="send-button button primary", type="submit"),
                    hx_post="/games/create",
                    hx_target="#form-alerts",
                ),
            ),
            cls="container",
        ),
    )


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


SCROLL_ON_MESSAGE_SCRIPT = """
let lastUpdate = 0
document.addEventListener("htmx:wsAfterMessage", e => {
    const now = Date.now().valueOf();
    const passed = now - lastUpdate;
    lastUpdate = now;
    const messagesDiv = document.querySelector(".game-content-container");
    const diff = messagesDiv.scrollHeight - messagesDiv.scrollTop - messagesDiv.clientHeight;
    if (diff < 200 || passed > 1000) {
        messagesDiv.scrollTop = messagesDiv.scrollHeight - messagesDiv.clientHeight ;
    }

})
"""


@rt("/game/{scenario_id}")
def get(scenario_id: str):

    corehtml = partial("core.html")
    return (
        Title("RNG"),
        NotStr(corehtml),
        NotStr('<script src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js"></script>'),
        Style(partial("css/game.css")),
        Div(
            navbar(),
            Div(
                Div(
                    id="game-content",
                ),
                cls="game-content-container",
            ),
            Script(SCROLL_ON_MESSAGE_SCRIPT),
            Form(
                Div(
                    game_input_area(),
                    Button("Send", cls="send-button button primary", type="submit"),
                    cls="input-area",
                ),
                ws_send="",
                hx_trigger="keyup[keyCode==13], submit",
                cls="input-form",
                id="game-input-form",
            ),
            hx_ext="ws",
            ws_connect=f"/ws/scenario/{scenario_id}",
            cls="game-container container",
        ),
    )


def game_input_area() -> Div:
    return Div(
        Textarea(
            id="game-input",
            name="game-input",
            placeholder="Enter an action",
            onInput="this.parentNode.dataset.replicatedValue = this.value",
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


async def websocket_handler(socket: WebSocket):
    scenario_id = socket.url.path.removeprefix("/ws/scenario/")

    async def send_msg(role: str, msg: str, id: Optional[str] = None) -> None:
        """Adds a single message"""
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

    async def stream_msg(role: str, generator: AsyncGenerator[str, None]) -> None:
        """streams a new single message"""
        id = "msg-" + str(uuid.uuid4())
        await send_msg(role, "", id=id)
        buff = ""
        async for msg in generator:
            buff += msg
            last_index = buff.rindex(" ") if " " in buff else 0
            to_send = buff[:last_index]
            buff = buff[last_index:]
            nodes = split_with_line_breaks(to_send)
            await socket.send_text(to_xml(Div(*nodes, id=id, hx_swap_oob="beforeend")))
        if buff:
            nodes = split_with_line_breaks(buff)
            await socket.send_text(to_xml(Div(*nodes, id=id, hx_swap_oob="beforeend")))

    try:
        await socket.accept()
        scenario = game.Game(scenario_id=scenario_id)
        did_any = False

        async def initialize():
            async for event in scenario.start_if_not_started_async():
                if type(event) == game.TextResponse:
                    yield event.delta

        await stream_msg("game", initialize())
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

                async def gen() -> AsyncGenerator[str, None]:
                    async for event in scenario.step_async(txt):
                        match event:
                            case game.TextResponse() as t:
                                yield t.delta

                await stream_msg("game", gen())

    except WebSocketDisconnect as e:
        pass


app.add_websocket_route("/ws/scenario/{scenario_id}", websocket_handler)

app.routes.append(
    Mount("/static", app=StaticFiles(directory="www/static"), name="static"),
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
