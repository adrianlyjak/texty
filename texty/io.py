from typing import Protocol
from rich.console import Console


class IOInterface(Protocol):
    def read_input(self, prompt: str) -> str:
        ...

    def write_output(self, message: str, end="\n") -> None:
        ...

class RichInterface(IOInterface):


    console = Console()

    def read_input(self, prompt: str) -> str:
        return self.console.input(prompt)

    def write_output(self, message: str, end="\n") -> None:
        self.console.print(message, end=end)

class StdIOInterface(IOInterface):
    def read_input(self, prompt: str) -> str:
        return input(prompt)

    def write_output(self, message: str, end="\n") -> None:
        print(message, end=end)from typing import List

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
