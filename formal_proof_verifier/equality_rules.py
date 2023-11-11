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

class EqualityEliminationRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()
        for line in self._lines:
            expected_dependencies.extend(line.dependencies)

        if not self._same_set(expected_dependencies, dependencies):
            return False

        equality_formula = self._lines[0].formula
        if equality_formula.type != FormulaType.predicate_type:
            return False

        if equality_formula.predicate != "=":
            return False

        variables: str = equality_formula.variables
        if len(variables) != 2:
            return False

        formula_a = self._lines[1].formula
        formula_b = current_line.formula
        if formula_a.eq_with_variable_map(formula_b, {variables[0]: variables[1]}):
            return True
        if formula_a.eq_with_variable_map(formula_b, {variables[1]: variables[0]}):
            return True

        return False

    def symbol() -> str:
        return "=E"

    def number_of_lines() -> int:
        return 2
