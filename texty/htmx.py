from fasthtml.common import *
import uvicorn

app = FastHTMLWithLiveReload()
rt = app.route


@rt("/")
def get():
    return Title("rnges.us"), Div(
        NotStr("<div>Hello Woild!</div>"), hx_get="/chat", hx_swap="afterend"
    )


@rt("/chat")
def get():
    return Div(
        NotStr("<div>This chat</div>"),
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", default=10666)))
