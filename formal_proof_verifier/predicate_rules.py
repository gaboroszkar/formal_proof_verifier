from typing import List
from .formula import FormulaType, Formula
from .rule import Rule
from .line import Line

class UniversalIntroductionRule(Rule):
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

        if current_line.formula.type != FormulaType.universal_type:
            return False

        inner_formula: Formula = current_line.formula.inner
        variable: str = current_line.formula.variable
        other_formula: Formula = self._lines[0].formula
        corresponding_variable: Optional[str] = (
            inner_formula.find_corresponding_variable(variable, other_formula)
        )

        if corresponding_variable:
            variable_map: Dict[str, str] = {variable: corresponding_variable}
            if inner_formula.eq_with_variable_map(other_formula, variable_map):
                for dependency in self._lines[0].dependencies:
                    if dependency.formula.is_variable_in(corresponding_variable):
                        return False
                return True
            else:
                return False
        else:
            return inner_formula == other_formula

    def symbol() -> str:
        return "UI"

    def number_of_lines() -> int:
        return 1

class UniversalEliminationRule(Rule):
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

        universal_formula: Formula = self._lines[0].formula
        if universal_formula.type != FormulaType.universal_type:
            return False

        inner_formula: Formula = universal_formula.inner
        variable: str = universal_formula.variable
        other_formula: Formula = current_line.formula
        corresponding_variable: Optional[str] = (
            inner_formula.find_corresponding_variable(variable, other_formula)
        )

        if corresponding_variable:
            variable_map: Dict[str, str] = {variable: corresponding_variable}
            return inner_formula.eq_with_variable_map(other_formula, variable_map)
        else:
            return inner_formula == other_formula

    def symbol() -> str:
        return "UE"

    def number_of_lines() -> int:
        return 1

class ExistentialIntroductionRule(Rule):
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

        if current_line.formula.type != FormulaType.existential_type:
            return False

        inner_formula: Formula = current_line.formula.inner
        variable: str = current_line.formula.variable
        other_formula: Formula = self._lines[0].formula
        corresponding_variable: Optional[str] = (
            inner_formula.find_corresponding_variable(variable, other_formula)
        )

        if corresponding_variable:
            variable_map: Dict[str, str] = {variable: corresponding_variable}
            return inner_formula.eq_with_variable_map(other_formula, variable_map)
        else:
            return inner_formula == other_formula

    def symbol() -> str:
        return "EI"

    def number_of_lines() -> int:
        return 1

class ExistentialEliminationRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()
        for line in self._lines:
            expected_dependencies.extend(line.dependencies)

        expected_dependencies = list(filter(
            lambda l: (l is not self._lines[1]),
            expected_dependencies
        ))

        if not self._same_set(expected_dependencies, dependencies):
            return False


        existential_formula: Formula = self._lines[0].formula
        if existential_formula.type != FormulaType.existential_type:
            return False

        if not self._lines[1].is_assumption():
            return False

        typical_disjunct_formula: Formula = self._lines[1].formula

        inner_formula: Formula = existential_formula.inner
        variable: str = existential_formula.variable
        corresponding_variable: Optional[str] = (
            inner_formula.find_corresponding_variable(variable, typical_disjunct_formula)
        )

        if corresponding_variable:
            variable_map: Dict[str, str] = {variable: corresponding_variable}
            if not inner_formula.eq_with_variable_map(typical_disjunct_formula, variable_map):
                return False

            if self._lines[2].formula.is_variable_in(corresponding_variable):
                return False

            for dependency in current_line.dependencies:
                if dependency.formula.is_variable_in(corresponding_variable):
                    return False
        elif inner_formula != typical_disjunct_formula:
            return False

        if self._lines[2].formula != current_line.formula:
            return False

        return True

    def symbol() -> str:
        return "EE"

    def number_of_lines() -> int:
        return 3

