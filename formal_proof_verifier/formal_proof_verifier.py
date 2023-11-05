import argparse
from re import split
from typing import Dict, Optional, List, Self, Union, Tuple
from enum import Enum
from abc import ABC, abstractmethod
from copy import copy

class FormulaType(Enum):
    atomic_type = 1
    and_type = 2
    or_type = 3
    conditional_type = 4
    not_type = 5
    predicate_type = 6
    universal_type = 7
    existential_type = 8

class StrRef:
    def __init__(self, s: Optional[str] = None):
        self.s = s

class Formula:
    def __init__(
        self,
        type: FormulaType,
        left: Optional[Self] = None,
        right: Optional[Self] = None,
        inner: Optional[Self] = None,
        atom: Optional[str] = None,
        predicate: Optional[str] = None,
        variable: Optional[str] = None,
        variables: Optional[List[str]] = None,
    ):
        self._type: FormulaType = type
        self._left: Optional[Self] = left
        self._right: Optional[Self] = right
        self._inner: Optional[Self] = inner
        self._atom: Optional[str] = atom
        self._predicate: Optional[str] = predicate
        self._variable: Optional[str] = variable
        self._variables: Optional[List[str]] = variables

    @property
    def type(self) -> FormulaType:
        return self._type

    @property
    def left(self) -> Optional[Self]:
        return self._left

    @property
    def right(self) -> Optional[Self]:
        return self._right

    @property
    def inner(self) -> Optional[Self]:
        return self._inner

    @property
    def atom(self) -> Optional[str]:
        return self._atom

    @property
    def predicate(self) -> Optional[str]:
        return self._predicate

    @property
    def variable(self) -> Optional[str]:
        return self._variable

    @property
    def variables(self) -> Optional[List[str]]:
        return self._variables

    @property
    def is_quantified(self) -> bool:
        return (
            self.type == FormulaType.universal_type or self.type == FormulaType.existential_type
        )

    @staticmethod
    def _eq_with_variable_map(self, other, variable_map: Dict[str, str]) -> bool:
        if not isinstance(self, Formula) and not isinstance(other, Formula):
            return self == other
        elif not isinstance(self, Formula) or not isinstance(other, Formula):
            return False
        else:
            if self.type != other.type:
                return False
            else:
                new_variable_map: Dict[str, str] = copy(variable_map)
                if self.is_quantified:
                    assert self.variable not in new_variable_map.keys()
                    new_variable_map[self.variable] = other.variable
                if (
                    Formula._eq_with_variable_map(self.left, other.left, new_variable_map)
                    and Formula._eq_with_variable_map(self.right, other.right, new_variable_map)
                    and Formula._eq_with_variable_map(self.inner, other.inner, new_variable_map)
                    and self.atom == other.atom
                    and self.predicate == other.predicate
                ):
                    if self.variable in new_variable_map:
                        if new_variable_map[self.variable] != other.variable:
                            return False
                    elif self.variable != other.variable:
                        return False

                    if self.variables is None or other.variables is None:
                        return self.variables == other.variables
                    else:
                        if len(self.variables) != len(other.variables):
                            return False
                        else:
                            for v, other_v in zip(self.variables, other.variables):
                                if v in new_variable_map:
                                    if new_variable_map[v] != other_v:
                                        return False
                                elif v != other_v:
                                    return False
                            return True
                else:
                    return False

    def eq_with_variable_map(self, other, variable_map) -> bool:
        return Formula._eq_with_variable_map(self, other, variable_map)

    def __eq__(self, other) -> bool:
        return self.eq_with_variable_map(other, {})

    @staticmethod
    def _find_corresponding_variable(
        self,
        variable: str,
        other: Optional[Self]
    ) -> Optional[str]:
        def _f(f1: Optional[Self], f2: Optional[Self]) -> Optional[str]:
            return Formula._find_corresponding_variable(f1, variable, f2)

        if self is None or other is None:
            return None

        if (corresponding_variable := _f(self.left, other.left)) is not None:
            return corresponding_variable
        if (corresponding_variable := _f(self.right, other.right)) is not None:
            return corresponding_variable
        if (corresponding_variable := _f(self.inner, other.inner)) is not None:
            return corresponding_variable

        if self.variable == variable:
            return other.variable
        else:
            if self.variables is None or other.variables is None:
                return None
            else:
                if len(self.variables) != len(other.variables):
                    return None
                else:
                    for v, other_v in zip(self.variables, other.variables):
                        if v == variable:
                            return other_v
                    return None

    def find_corresponding_variable(self, variable: str, other: Self) -> Optional[str]:
        return Formula._find_corresponding_variable(self, variable, other)

    def is_variable_in(self, variable: str) -> bool:
        def _is_variable_in(f: Optional[Self]) -> bool:
            if f is None:
                return False
            else:
                return f.is_variable_in(variable)

        if _is_variable_in(self.left):
            return True
        elif _is_variable_in(self.right):
            return True
        elif _is_variable_in(self.inner):
            return True
        elif self.variable == variable:
            return True
        elif (
            self.variables is not None
            and any(v == variable for v in self.variables)
        ):
            return True
        else:
            return False

    def __str__(self) -> str:
        if self.type == FormulaType.atomic_type:
            return self.atom
        elif self.type == FormulaType.and_type:
            return "(" + str(self.left) + ")&(" + str(self.right) + ")"
        elif self.type == FormulaType.or_type:
            return "(" + str(self.left) + ")v(" + str(self.right) + ")"
        elif self.type == FormulaType.conditional_type:
            return "(" + str(self.left) + ")>(" + str(self.right) + ")"
        elif self.type == FormulaType.not_type:
            return "~(" + str(self.inner) + ")"
        elif self.type == FormulaType.predicate_type:
            return self.predicate + "(" + ",".join(self.variables) + ")"
        elif self.type == FormulaType.universal_type:
            return "A(" + self.variable + ")(" + str(self.inner) + ")"
        elif self.type == FormulaType.existential_type:
            return "E(" + self.variable + ")(" + str(self.inner) + ")"
        else:
            return "INVALID"

def tokenize(formula_str: str) -> list[Union[str, FormulaType]]:
    if len(formula_str) == 0:
        raise RuntimeError("Error: empty formula.")

    connectives_to_type: Dict[str, FormulaType] = {
        "&": FormulaType.and_type,
        "v": FormulaType.or_type,
        ">": FormulaType.conditional_type,
        "~": FormulaType.not_type,
        "A": FormulaType.universal_type,
        "E": FormulaType.existential_type,
    }

    tokens: List[Union[str, FormulaType]] = []

    s: Optional[str] = None
    depth: int = 0
    for c in formula_str:
        if c == "(":
            depth += 1
            if depth == 1:
                if s is not None:
                    tokens.append(s)
                s = ""
            else:
                s += c
        elif c == ")":
            depth -= 1
            if depth == 0:
                assert s is not None
                tokens.append(s)
                s = None
            elif depth < 0:
                raise RuntimeError(f"Error: unexpected ')' in formula '{formula_str}'.")
            else:
                s += c
        elif depth == 0:
            if c in connectives_to_type or c == "=":
                if s is not None:
                    tokens.append(s)
                    s = None
                if c in connectives_to_type:
                    tokens.append(connectives_to_type[c])
                else:
                    tokens.append(c)
            else:
                if s is None:
                    s = ""
                s += c
        else:
            s += c

    if s is not None:
        tokens.append(s)
        s = None

    assert len(tokens) != 0

    return tokens

def group_tokens(tokens: List[Union[str, FormulaType]]) -> List[Union[List[str], FormulaType]]:
    grouped_tokens: List[Union[List[str], FormulaType]] = []
    current_str_group: Optional[List[str]] = None
    for token in tokens:
        if isinstance(token, FormulaType):
            if current_str_group is not None:
                grouped_tokens.append(current_str_group)
                current_str_group = None
            grouped_tokens.append(token)
        else:
            if current_str_group is None:
                current_str_group = []
            current_str_group.append(token)

    if current_str_group is not None:
        grouped_tokens.append(current_str_group)

    return grouped_tokens

def create_constituents(
    grouped_tokens: List[Union[List[str], FormulaType]],
    reserved_variables: List[str]
) -> List[Union[Formula, FormulaType]]:
    constituents: List[Union[Formula, FormulaType]] = []

    for grouped_token in grouped_tokens:
        if isinstance(grouped_token, FormulaType):
            constituents.append(grouped_token)
        else:
            if len(grouped_token) == 1:
                constituents.append(
                    _create_formula(grouped_token[0], reserved_variables)
                )
            elif len(grouped_token) == 2:
                constituents.append(Formula(
                    type=FormulaType.predicate_type,
                    predicate=grouped_token[0],
                    variables=grouped_token[1].split(",")
                ))
            elif len(grouped_token) == 3:
                variable_left: str = grouped_token[0]
                predicate: str = grouped_token[1]
                variable_right: str = grouped_token[2]

                constituents.append(Formula(
                    type=FormulaType.predicate_type,
                    predicate=predicate,
                    variables=[variable_left, variable_right]
                ))
            else:
                raise RuntimeError(
                    f"Error: formula has more than 3 tokens "
                    f"next to each other without any connective: "
                    f"'{grouped_token}'."
                )

    return constituents

def create_unquantified_formula(
    tokens: List[Union[str, FormulaType]],
    reserved_variables: List[str]
) -> Formula:
    grouped_tokens: List[Union[List[str], FormulaType]] = group_tokens(tokens)
    constituents: List[Union[Formula, FormulaType]] = (
        create_constituents(grouped_tokens, reserved_variables)
    )

    biconnectives = {
        FormulaType.and_type,
        FormulaType.or_type,
        FormulaType.conditional_type,
    }
    uniconnectives = {
        FormulaType.not_type,
    }
    if any(c in constituents for c in biconnectives):
        if len(constituents) != 3:
            raise RuntimeError(
                "Error: main connective is a biconnective, "
                "but the number of constituents are not 3."
            )
        connective = constituents[1]
        if connective not in biconnectives:
            raise RuntimeError(
                "Error: main connective is a biconnective, "
                "but it's not the 2nd constituent."
            )
        left_formula = constituents[0]
        right_formula = constituents[2]
        return Formula(type=connective, left=left_formula, right=right_formula)
    elif any(c in constituents for c in uniconnectives):
        if len(constituents) != 2:
            raise RuntimeError(
                "Error: main connective is a uniconnective, "
                "but the number of constituents are not 2."
            )
        connective = constituents[0]
        if connective not in uniconnectives:
            raise RuntimeError(
                "Error: main connective is a uniconnective, "
                "but it's not the 1st constituent."
            )
        inner_formula = constituents[1]
        return Formula(type=connective, inner=inner_formula)
    else:
        if len(constituents) == 1 and isinstance(constituents[0], Formula):
            return constituents[0]
        else:
            raise RuntimeError(
                f"Error: formula '{formula_str}' cannot be interpreted."
            )

def _create_formula(formula_str: str, reserved_variables: List[str]) -> Formula:
    tokens: List[Union[str, FormulaType]] = tokenize(formula_str)

    if len(tokens) == 1:
        token = tokens[0]
        if isinstance(token, FormulaType):
            raise RuntimeError(
                f"Error: formula '{formula_str}' has one constituent, "
                f"and it is a connective ('{token}')."
            )
        else:
            inner_tokens = tokenize(token)
            # Check if token is atomic i.e. cannot be broken down even more.
            if len(inner_tokens) == 1 and inner_tokens[0] == token:
                return Formula(type=FormulaType.atomic_type, atom=token)
            else:
                return _create_formula(token, reserved_variables)
    else:
        assert len(tokens) != 0

        if tokens[0] == FormulaType.universal_type or tokens[0] == FormulaType.existential_type:
            if len(tokens) < 3:
                raise RuntimeError(
                    f"Error: formula '{formula_str}' if quantified, but "
                    f"missing the variable or the formula to be quantified."
                )
            variable: str = tokens[1]
            if variable in reserved_variables:
                raise RuntimeError(
                    f"Error: formula '{formula_str}' has an already used "
                    f"quantified variable '{variable}'."
                )
            new_reserved_variables: List[str] = copy(reserved_variables)
            new_reserved_variables.append(variable)
            return Formula(
                type=tokens[0],
                variable=variable,
                inner=create_unquantified_formula(tokens[2:], new_reserved_variables)
            )
        else:
            return create_unquantified_formula(tokens, reserved_variables)

def create_formula(formula_str: str) -> Formula:
    """
    Breaks down the formula string into tokens, and then to constituents,
    and then creates a formula.
    Each token is either a string or a connective. Each string represents
    a predicate or list of variables or formula itself.
    Here, we first figure out whether the tokens are just an atomic formula.
    If not, the rule to create the constituents is that each consequtive string token
    is considered as a predicate and a list of variables. Otherwise, we keep the
    original token as a connective, or we process it as a formula.
    Sidenote: when we process a list of variables, we don't care about the parenthesis,
    they are always split into multiple variables by the commas.
    """
    return _create_formula(formula_str, [])

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
        variable_map: Dict[str, str] = (
            {variable: corresponding_variable} if corresponding_variable else {}
        )

        return inner_formula.eq_with_variable_map(other_formula, variable_map)

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
            if self._lines[2].formula.is_variable_in(corresponding_variable):
                return False

            for dependency in current_line.dependencies:
                if dependency.formula.is_variable_in(corresponding_variable):
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
