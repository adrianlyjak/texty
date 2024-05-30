from typing import Protocol


class IOInterface(Protocol):
    def read_input(self, prompt: str) -> str:
        ...

    def write_output(self, message: str) -> None:
        ...

class StdIOInterface(IOInterface):
    def read_input(self, prompt: str) -> str:
        return input(prompt)

    def write_output(self, message: str) -> None:
        print(message)