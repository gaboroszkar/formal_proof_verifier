from typing import List, Self
from .formula import Formula
from .rule import Rule

class Line:
    def __init__(
        self,
        dependencies: List[Self],
        formula: Formula,
        rule: Rule,
        is_self_dependency: bool
    ):
        self._dependencies: List[Self] = dependencies
        self._formula: Formula = formula
        self._rule: Rule = rule

        if is_self_dependency:
            self._dependencies.append(self)

    @property
    def dependencies(self) -> List[Self]:
        return self._dependencies

    @property
    def formula(self) -> Formula:
        return self._formula

    def is_assumption(self) -> bool:
        return self._rule.is_assumption()

    def is_valid(self) -> bool:
        return self._rule.is_valid(
            current_line=self,
        )

