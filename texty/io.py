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
        print(message, end=end)