from typing import List
from .formula import FormulaType, Formula
from .rule import Rule
from .line import Line

class EqualityIntroductionRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()

        if not self._same_set(expected_dependencies, dependencies):
            return False

        if current_line.formula.type != FormulaType.predicate_type:
            return False

        predicate: str = current_line.formula.predicate
        if predicate != "=":
            return False

        variables: str = current_line.formula.variables
        if len(variables) != 2:
            return False
        if variables[0] != variables[1]:
            return False

        return True

    def symbol() -> str:
        return "=I"

    def number_of_lines() -> int:
        return 0
