from fasthtml.common import Nav, Div, A, NotStr, H1


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
