from typing import List

from formal_proof_verifier import create_lines_from_text

def map_is_valid(text: str) -> List[bool]:
    lines: List[Union[str, Line]] = create_lines_from_text(text)
    return [line[1].is_valid() for line in lines]
