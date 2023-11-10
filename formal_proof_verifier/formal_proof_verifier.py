from re import split
from typing import Dict, Optional, List, Self, Tuple
from .formula import Formula, FormulaType, create_formula
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

class PremiseRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        return (
            len(dependencies) == 1
            and next(iter(dependencies)) is current_line
        )

    def symbol() -> str:
        return "P"

    def number_of_lines() -> int:
        return 0

class AssumptionRule(Rule):
    @staticmethod
    def is_assumption() -> bool:
        return True

    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        return (
            len(dependencies) == 1
            and next(iter(dependencies)) is current_line
        )

    def symbol() -> str:
        return "A"

    def number_of_lines() -> int:
        return 0

class AndIntroductionRule(Rule):
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

        if current_line.formula.type != FormulaType.and_type:
            return False

        if self._lines[0].formula != current_line.formula.left:
            return False

        if self._lines[1].formula != current_line.formula.right:
            return False

        return True

    def symbol() -> str:
        return "&I"

    def number_of_lines() -> int:
        return 2

class AndEliminationRule(Rule):
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

        if self._lines[0].formula.type != FormulaType.and_type:
            return False

        if self._lines[0].formula.left == current_line.formula:
            return True

        if self._lines[0].formula.right == current_line.formula:
            return True

        return False

    def symbol() -> str:
        return "&E"

    def number_of_lines() -> int:
        return 1

class OrIntroductionRule(Rule):
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

        if current_line.formula.type != FormulaType.or_type:
            return False

        if self._lines[0].formula == current_line.formula.left:
            return True

        if self._lines[0].formula == current_line.formula.right:
            return True

        return False

    def symbol() -> str:
        return "vI"

    def number_of_lines() -> int:
        return 1

class OrEliminationRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()
        for line in self._lines:
            expected_dependencies.extend(line.dependencies)

        expected_dependencies = list(filter(
            lambda l: (l is not self._lines[1] and l is not self._lines[3]),
            expected_dependencies
        ))

        if not self._same_set(expected_dependencies, dependencies):
            return False

        if self._lines[0].formula.type != FormulaType.or_type:
            return False

        if not self._lines[1].is_assumption():
            return False
        if self._lines[1].formula != self._lines[0].formula.left:
            return False

        if self._lines[1] not in self._lines[2].dependencies:
            return False
        if self._lines[2].formula != current_line.formula:
            return False

        if not self._lines[3].is_assumption():
            return False
        if self._lines[3].formula != self._lines[0].formula.right:
            return False

        if self._lines[3] not in self._lines[4].dependencies:
            return False
        if self._lines[4].formula != current_line.formula:
            return False

        return True

    def symbol() -> str:
        return "vE"

    def number_of_lines() -> int:
        return 5

class CPRule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()
        for line in self._lines:
            expected_dependencies.extend(line.dependencies)

        expected_dependencies = list(filter(
            lambda l: (l is not self._lines[0]),
            expected_dependencies
        ))

        if not self._same_set(expected_dependencies, dependencies):
            return False

        if current_line.formula.type != FormulaType.conditional_type:
            return False

        if not self._lines[0].is_assumption():
            return False

        if self._lines[0] not in self._lines[1].dependencies:
            return False

        if self._lines[0].formula != current_line.formula.left:
            return False

        if self._lines[1].formula != current_line.formula.right:
            return False

        return True

    def symbol() -> str:
        return "CP"

    def number_of_lines() -> int:
        return 2

class ModusPonensRule(Rule):
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

        if self._lines[0].formula.type != FormulaType.conditional_type:
            return False

        if self._lines[0].formula.left != self._lines[1].formula:
            return False

        if self._lines[0].formula.right != current_line.formula:
            return False

        return True

    def symbol() -> str:
        return "MP"

    def number_of_lines() -> int:
        return 2

class DNIRule(Rule):
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

        if current_line.formula.type != FormulaType.not_type:
            return False

        if current_line.formula.inner.type != FormulaType.not_type:
            return False

        if self._lines[0].formula != current_line.formula.inner.inner:
            return False

        return True

    def symbol() -> str:
        return "DNI"

    def number_of_lines() -> int:
        return 1

class DNERule(Rule):
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

        if self._lines[0].formula.type != FormulaType.not_type:
            return False

        if self._lines[0].formula.inner.type != FormulaType.not_type:
            return False

        if self._lines[0].formula.inner.inner != current_line.formula:
            return False

        return True

    def symbol() -> str:
        return "DNE"

    def number_of_lines() -> int:
        return 1

class ModusTollensRule(Rule):
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

        if self._lines[0].formula.type != FormulaType.conditional_type:
            return False

        if self._lines[1].formula.type != FormulaType.not_type:
            return False

        if current_line.formula.type != FormulaType.not_type:
            return False

        if self._lines[0].formula.right != self._lines[1].formula.inner:
            return False

        if self._lines[0].formula.left != current_line.formula.inner:
            return False

        return True

    def symbol() -> str:
        return "MT"

    def number_of_lines() -> int:
        return 2

class RAARule(Rule):
    def _is_valid(
        self,
        dependencies: List[Line],
        current_line: Line,
    ) -> bool:
        expected_dependencies = list()
        for line in self._lines:
            expected_dependencies.extend(line.dependencies)

        expected_dependencies = list(filter(
            lambda l: (l is not self._lines[0]),
            expected_dependencies
        ))

        if not self._same_set(expected_dependencies, dependencies):
            return False

        if not self._lines[0].is_assumption():
            return False

        if self._lines[0] not in self._lines[1].dependencies:
            return False

        if self._lines[1].formula.type != FormulaType.and_type:
            return False

        if self._lines[1].formula.right.type != FormulaType.not_type:
            return False

        if self._lines[1].formula.left != self._lines[1].formula.right.inner:
            return False

        if current_line.formula.type != FormulaType.not_type:
            return False

        if self._lines[0].formula != current_line.formula.inner:
            return False

        return True

    def symbol() -> str:
        return "RAA"

    def number_of_lines() -> int:
        return 2

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

def create_lines(lines_str: List[str]) -> List[Tuple[str, Line]]:
    lines: Dict[str, Tuple[str, Line]] = {}

    for line_str in lines_str:
        unformatted_line_str = line_str

        line_str = line_str.split(sep="#", maxsplit=1)
        line_str = line_str[0]
        line_str = line_str.strip(" ")
        line_str = split(" +", line_str)

        if (len(line_str) == 4 or len(line_str) == 5):
            dependencies_str: List[str] = line_str[0].split(",")
            line_number_str: str = line_str[1]
            formula_str: str = line_str[2]
            rule_symbol: str = line_str[4] if len(line_str) == 5 else line_str[3]
            rule_lines_str: List[str] = line_str[3].split(",") if len(line_str) == 5 else []

            empty_dependency: str = "-"

            if line_number_str == empty_dependency:
                raise RuntimeError(f"Error: Line number cannot be '{line_number_str}'.")

            if line_number_str in lines:
                raise RuntimeError(f"Error: Line number '{line_number_str}' already exists.")

            formula: Formula = create_formula(formula_str)

            if any(l not in lines for l in rule_lines_str):
                raise RuntimeError(f"Error: Invalid line number for rule in '{unformatted_line_str}'.")
            rule_lines: List[Line] = [lines[l][1] for l in rule_lines_str]
            rule = Rule.create(symbol=rule_symbol, lines=rule_lines)

            dependencies_str = list(filter(lambda x: x != empty_dependency, dependencies_str))
            if any((l != line_number_str and l not in lines) for l in dependencies_str):
                raise RuntimeError(f"Error: Invalid line number for dependencies in '{unformatted_line_str}'.")
            dependencies: List[Line] = [lines[l][1] for l in dependencies_str if l != line_number_str]

            is_self_dependency: bool = (line_number_str in dependencies_str)

            line: Line = Line(dependencies=dependencies, formula=formula, rule=rule, is_self_dependency=is_self_dependency)
            lines[line_number_str] = (unformatted_line_str, line)
        else:
            raise RuntimeError(f"Error: Invalid line '{unformatted_line_str}'.")
    return lines.values()

def create_lines_from_text(text: str) -> List[Tuple[str, Line]]:
    text = text.split("\n")
    lines_str: List[str] = []
    for unformatted_line_str in text:
        line_str = unformatted_line_str

        line_str = line_str.split(sep="#", maxsplit=1)
        line_str = line_str[0]
        line_str = line_str.strip(" ")
        if line_str != "":
            lines_str.append(unformatted_line_str)
    return create_lines(lines_str)
