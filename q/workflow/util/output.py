from typing import Protocol, Self, runtime_checkable

@runtime_checkable
class Printable(Protocol):
    def __str__(self) -> str:
        ...

class Printer(Protocol):
    def set_title(self, title: str) -> Self:
        ...

    def print(self, any: Printable) -> None:
        ...
        

class DefaultPrinter:
    def print(self, any: Printable) -> None:
        print(any)
        
    def set_title(self, title: str) -> Self:
        return self  # never used