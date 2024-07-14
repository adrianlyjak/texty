import asyncio
import datetime
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fasthtml.common import *
import starlette
import starlette.requests
import secrets
import os
from texty import database
from texty import game
from texty.gametypes import LogItem
from texty.navbar import navbar

app = FastHTMLWithLiveReload()
rt = app.route


def partial(path: str) -> str:
    with open(os.path.join("www", "partial", path), "r") as f:
        return f.read()


def navbar() -> Nav:
    return Nav(
        Div(
            A(
                NotStr(
                    """<svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,10 85,30 85,70 50,90 15,70 15,30" stroke="black" stroke-width="2" fill="white"/>
</svg>
"""
                ),
                href="/",
            ),
            style="display: flex; align-items: center; justify-content: center; padding-right: 0.5rem; padding-bottom: 1rem;",
        ),
        H1("RNGes.us"),
        cls="header",
    )


def page(*children):
    corehtml = partial("core.html")
    return (
        Title("RNGes.us"),
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

    return page(
        Main(
            H2("Load Game"),
            *[
                A(
                    Div(
                        f"{timestamp.strftime("%Y-%m-%d %H:%m:%S %p")} - {game.summary}",
                    ),
                    href="/game/" + game.scenario_id(),
                )
                for timestamp, game in games
            ],
        ),
    )


@rt("/games/create")
def get():
    corehtml = partial("core.html")

    return (
        Title("RNGes.us"),
        NotStr(corehtml),
        Main(
            navbar(),
            cls="container",
        ),
    )


@rt("/game/{scenario_id}")
def get(scenario_id: str):

    return page(
        Main(
            Style(partial("css/game.css")),
            Div(
                Div(
                    id="game-content",
                ),
                cls="game-content-container",
            ),
            Form(
                Div(
                    game_input_area(),
                    Button("Send", cls="send-button button primary", type="submit"),
                    cls="input-area",
                ),
                ws_send="",
            ),
            hx_ext="ws",
            ws_connect=f"/ws/scenario/{scenario_id}",
        )
    )


def game_input_area() -> Div:
    return Div(
        Textarea(
            id="game-input",
            placeholder="Enter your action...",
            onInput="this.parentNode.dataset.replicatedValue = this.value",
        ),
        cls="grow-wrap",
        id="game-input-area",
    )


def game_message(event: LogItem) -> Div:
    texts = [P(txt) for txt in event.text.split("\n")]
    return Div(
        *texts,
        cls="game-message-player" if event.role == "player" else "game-message-game",
    )


async def websocket_handler(socket: WebSocket, *args):
    scenario_id = socket.url.path.removeprefix("/ws/scenario/")

    try:
        await socket.accept()
        scenario = game.Game(scenario_id=scenario_id)
        did_any = False
        for event in scenario.start_if_not_started():
            if type(event) == game.TextResponse:
                await socket.send_text(to_xml(Div(event.full_text, id="game-content")))
        if not did_any:
            log = []
            for event in scenario.node.event_log:
                if event.role != "internal":
                    log.append(game_message(event))

            await socket.send_text(to_xml(Div(*log, id="game-content")))

        while True:
            message = await socket.receive_json()
            txt = message.get("game-input", "").strip()
            await socket.send_text(to_xml(game_input_area()))
            if txt == "/undo":
                if scenario.undo():
                    await socket.send_text(
                        to_xml(Div("Undo successful", id="game-content"))
                    )
                else:
                    await socket.send_text(
                        to_xml(Div("Undo failed", id="game-content"))
                    )
            elif txt:
                for event in scenario.step(txt):
                    match event:
                        case game.TextResponse() as t:
                            await socket.send_text(
                                to_xml(Div(t.full_text, id="game-content"))
                            )

    except WebSocketDisconnect as e:
        pass


app.add_websocket_route("/ws/scenario/{scenario_id}", websocket_handler)
app.routes.append(
    Mount("/static", app=StaticFiles(directory="www/static"), name="static"),
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
