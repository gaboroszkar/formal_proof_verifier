from re import split
from typing import Dict, List, Tuple
from .formula import Formula, create_formula
from .rule import Rule
from .line import Line
from .propositional_rules import *
from .predicate_rules import *

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
