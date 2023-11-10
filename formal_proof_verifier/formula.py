from re import split
from typing import Dict, Optional, List, Self, Union
from enum import Enum
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
