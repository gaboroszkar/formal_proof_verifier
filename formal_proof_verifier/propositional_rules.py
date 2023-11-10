from typing import List
from .formula import FormulaType
from .rule import Rule
from .line import Line

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

