import pytest
from typing import List

from formal_proof_verifier import create_lines_from_text

def _map_is_valid(text: str) -> List[bool]:
    lines: List[Union[str, Line]] = create_lines_from_text(text)
    return [line[1].is_valid() for line in lines]

def test_and_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1     1 P           P
        2     2 Q           P
        3     3 R           P
        1,2   4 P&Q         &I 1,2
        2,3   5 Q&R         &I 2,3
        1,2,3 6 (Q&R)&(P&Q) &I 5,4
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   P
        3   3 R   P
        1,2 4 P&Q &I 1
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   P
        3   3 R   P
        1,2 4 P&Q &I 1,2,3
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P           P
        2   2 Q           P
        3   3 R           P
        1,2 4 P&Q         &I 1,2
        2,3 5 Q&R         &I 2,3
        1,2 6 (Q&R)&(P&Q) &I 5,4
        2,3 7 (Q&R)&(P&Q) &I 5,4
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 P   P
        2     2 Q   P
        3     3 R   P
        1,2,3 4 P&Q &I 1,2
        1,2,3 5 Q&R &I 2,3
    """
    assert _map_is_valid(text) == [True, True, True, False, False]

    # Incorrect connective.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 PvQ &I 1,2
    """
    assert _map_is_valid(text) == [True, True, False]

    # Left formula is not the same.
    text: str = """
        1     1 P           P
        2     2 Q           P
        3     3 R           P
        1,2   4 P&Q         &I 1,2
        2,3   5 Q&R         &I 2,3
        1,2,3 6 (R&R)&(P&Q) &I 5,4
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Right formula is not the same.
    text: str = """
        1     1 P           P
        2     2 Q           P
        3     3 R           P
        1,2   4 P&Q         &I 1,2
        2,3   5 Q&R         &I 2,3
        1,2,3 6 (Q&R)&(Q&Q) &I 5,4
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]
