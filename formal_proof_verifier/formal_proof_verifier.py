from re import split
from typing import Dict, Optional, List, Self, Tuple
from abc import ABC, abstractmethod
from .formula import Formula, FormulaType, create_formula

class Rule(ABC):
    @staticmethod
    def create(symbol: str, lines: list) -> Self:
        symbol_to_cls: dict = {
            "P": (PremiseRule, 0),
            "A": (AssumptionRule, 0),
            "&I": (AndIntroductionRule, 2),
            "&E": (AndEliminationRule, 1),
            "vI": (OrIntroductionRule, 1),
            "vE": (OrEliminationRule, 5),
            "CP": (CPRule, 2),
            "MP": (ModusPonensRule, 2),
            "DNI": (DNIRule, 1),
            "DNE": (DNERule, 1),
            "MT": (ModusTollensRule, 2),
            "RAA": (RAARule, 2),
            "UI": (UniversalIntroductionRule, 1),
            "UE": (UniversalEliminationRule, 1),
            "EI": (ExistentialIntroductionRule, 1),
            "EE": (ExistentialEliminationRule, 3),
        }

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
    def is_assumption():
        return False

    @abstractmethod
    def _is_valid(
        self,
        dependencies: list,
        current_line,
    ) -> bool:
        # Check if formula is the consequence,
        # and check if the dependency formulas are the same.
        pass

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

class AssumptionRule(Rule):
    @staticmethod
    def is_assumption():
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
