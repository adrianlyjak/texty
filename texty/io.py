import sys
from typing import Any, Iterator, Protocol
from typing import List
from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text



class IOInterface(Protocol):
    def read_input(self, prompt: str) -> str:
        ...

    def write_output(self, message: str, end="\n") -> None:
        ...

    def live_panel(self, initial_text: str) -> "Panel":
        ...


class Panel(Protocol):
    def update(self, text: str) -> None:
        ...

    def __enter__(self) -> "Panel":
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...
    

class RichInterface(IOInterface):


    console = Console()

    def read_input(self, prompt: str) -> str:
        return self.console.input(prompt)

    def write_output(self, message: str, end="\n") -> None:
        self.console.print(message, end=end)

    def live_panel(self, initial_text: str) -> Panel:
        return RichPanel(self.console, initial_text)

class RichPanel():
    def __init__(self, console: Console, initial_text: str) -> None:
        self.text = Text(initial_text)
        self.console = console
    
    def __enter__(self) -> "RichPanel":
        self.live = Live(self.text, console=self.console, refresh_per_second=10)
        self.live.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.live.__exit__(exc_type, exc_value, traceback)


    def update(self, text: str | RenderableType) -> None:
        self.text = Text(text) if type(text) is str else text
        self.live.update(self.text)

    
def list_choice(io: IOInterface, prompt: str, choices: List[str]) -> int:
    """
    Display a list of choices and prompt the user to select one.

    Args:
        io (IOInterface): The IO interface to use for input/output.
        prompt (str): The prompt to display to the user.
        choices (List[str]): The list of choices to display.

    Returns:
        int: The index of the selected choice (1-based index).
    """
    while True:
        for idx, choice in enumerate(choices, start=1):
            io.write_output(f"{idx}. {choice}")
        selection = io.read_input(prompt).strip()
        if selection.isdigit() and 1 <= int(selection) <= len(choices):
            return int(selection)
        else:
            io.write_output("Invalid choice. Please select a valid option.")
