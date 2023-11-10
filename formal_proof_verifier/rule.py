from typing import List, Self
from abc import ABC, abstractmethod

def append_all_subclasses(cls, subclasses: list) -> None:
    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        append_all_subclasses(subclass, subclasses)
def subclasses(cls) -> list:
    result = []
    append_all_subclasses(cls, result)
    return result

class Rule(ABC):
    @staticmethod
    def create(symbol: str, lines: list) -> Self:
        symbol_to_cls: dict = {}
        for sub_cls in subclasses(Rule):
            symbol_to_cls[sub_cls.symbol()] = (sub_cls, sub_cls.number_of_lines())

        if symbol not in symbol_to_cls:
            raise RuntimeError(f"Error: rule '{symbol}' is invalid.")
        cls, number_of_lines = symbol_to_cls[symbol]
        if number_of_lines != len(lines):
            raise RuntimeError(f"Error: rule '{symbol}' has invalid number of line numbers.")

        return cls(lines)

    def __init__(
        self,
        lines: list,
    ):
        self._lines = lines

    def is_valid(
        self,
        current_line,
    ) -> bool:
        if any((l is not current_line and not l.is_valid()) for l in self._lines):
            return False
        return self._is_valid(dependencies=current_line.dependencies, current_line=current_line)

    @staticmethod
    def _same_set(set_1: List, set_2: List):
        def _is_in(x, set: List):
            return any(x is e for e in set)

        def _all_is_in(set_a: List, set_b: List):
            return all(_is_in(x, set_b) for x in set_a)

        return _all_is_in(set_1, set_2) and _all_is_in(set_2, set_1)

    @staticmethod
    def is_assumption() -> bool:
        return False

    @staticmethod
    def symbol() -> str:
        pass

    @staticmethod
    def number_of_lines() -> int:
        pass

    @abstractmethod
    def _is_valid(
        self,
        dependencies: list,
        current_line,
    ) -> bool:
        # Check if formula is the consequence,
        # and check if the dependency formulas are the same.
        pass
