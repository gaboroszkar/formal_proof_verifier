import pytest
from typing import List

from formal_proof_verifier import create_lines_from_text

def _map_is_valid(text: str) -> List[bool]:
    lines: List[Union[str, Line]] = create_lines_from_text(text)
    return [line[1].is_valid() for line in lines]

def test_premise_rule():
    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R>S) P
        2 2 P>(~(Q>S))  P
    """
    assert _map_is_valid(text) == [True, True]

    # Too many line numbers for the rule.
    text: str = """
        1 1 (P&Q)v(R>S) P
        2 2 P>(~(Q>S))  P 1
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Incorrect dependency.
    text: str = """
        1 1 (P&Q)v(R>S) P
        1 2 P>(~(Q>S))  P
    """
    assert _map_is_valid(text) == [True, False]

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R>S) P
        - 2 P>(~(Q>S))  P
    """
    assert _map_is_valid(text) == [True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R>S) P
        1,2 2 P>(~(Q>S))  P
    """
    assert _map_is_valid(text) == [True, False]

def test_assumption_rule():
    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R>S) A
        2 2 P>(~(Q>S))  A
    """
    assert _map_is_valid(text) == [True, True]

    # Too many line numbers for the rule.
    text: str = """
        1 1 (P&Q)v(R>S) A
        2 2 P>(~(Q>S))  A 1
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Incorrect dependency.
    text: str = """
        1 1 (P&Q)v(R>S) A
        1 2 P>(~(Q>S))  A
    """
    assert _map_is_valid(text) == [True, False]

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R>S) A
        - 2 P>(~(Q>S))  A
    """
    assert _map_is_valid(text) == [True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R>S) A
        1,2 2 P>(~(Q>S))  A
    """
    assert _map_is_valid(text) == [True, False]

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

def test_and_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P&Q P
        1 2 P   &E 1
        1 3 Q   &E 1
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) &I 2,1
        1,2 4 P&Q         &E 3
        1,2 5 P           &E 4
        1,2 6 Q           &E 4
        1,2 7 Q&R         &E 3
        1,2 8 Q           &E 7
        1,2 9 R           &E 7
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 P&Q P
        1 2 P   &E
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 P&Q P
        2 2 R   P
        1 3 P   &E 1,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) &I 2,1
        1   4 P&Q         &E 3
        2   5 Q&R         &E 3
    """
    assert _map_is_valid(text) == [True, True, True, False, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 Q&R         P
        2     2 P&Q         P
        1,2   3 (P&Q)&(Q&R) &I 2,1
        1,2,3 4 P&Q         &E 3
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 PvQ P
        1 2 P   &E 1
    """
    assert _map_is_valid(text) == [True, False]

    # None of the formulas are the same.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) &I 2,1
        1,2 4 P&P         &E 3
    """
    assert _map_is_valid(text) == [True, True, True, False]

def test_or_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P       P
        1 2 PvQ     vI 1
        1 3 Rv(PvQ) vI 2
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     &I 1,2
        1,2 4 Rv(P&Q) vI 3
    """
    assert _map_is_valid(text) == [True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 P   P
        2 2 Q   P
        1 2 PvQ vI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 P       P
        1 2 PvQ     vI 1
        1 3 Rv(PvQ) vI 1,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     &I 1,2
        2   4 Rv(P&Q) vI 3
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 PvQ vI 1
    """
    assert _map_is_valid(text) == [True, True, False]

    # None of the formulas are the same.
    text: str = """
        1 1 P   P
        2 2 Q   P
        2 3 PvP vI 2
    """
    assert _map_is_valid(text) == [True, True, False]
