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
        2 2 P>(~(Q>S))  1 A
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
        1,2   4 P&Q         1,2 &I
        2,3   5 Q&R         2,3 &I
        1,2,3 6 (Q&R)&(P&Q) 5,4 &I
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   P
        3   3 R   P
        1,2 4 P&Q 1 &I
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   P
        3   3 R   P
        1,2 4 P&Q 1,2,3 &I
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P           P
        2   2 Q           P
        3   3 R           P
        1,2 4 P&Q         1,2 &I
        2,3 5 Q&R         2,3 &I
        1,2 6 (Q&R)&(P&Q) 5,4 &I
        2,3 7 (Q&R)&(P&Q) 5,4 &I
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 P   P
        2     2 Q   P
        3     3 R   P
        1,2,3 4 P&Q 1,2 &I
        1,2,3 5 Q&R 2,3 &I
    """
    assert _map_is_valid(text) == [True, True, True, False, False]

    # Incorrect connective.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 PvQ 1,2 &I
    """
    assert _map_is_valid(text) == [True, True, False]

    # Left formula is not the same.
    text: str = """
        1     1 P           P
        2     2 Q           P
        3     3 R           P
        1,2   4 P&Q         1,2 &I
        2,3   5 Q&R         2,3 &I
        1,2,3 6 (R&R)&(P&Q) 5,4 &I
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Right formula is not the same.
    text: str = """
        1     1 P           P
        2     2 Q           P
        3     3 R           P
        1,2   4 P&Q         1,2 &I
        2,3   5 Q&R         2,3 &I
        1,2,3 6 (Q&R)&(Q&Q) 5,4 &I
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

def test_and_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P&Q P
        1 2 P   1 &E
        1 3 Q   1 &E
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) 2,1 &I
        1,2 4 P&Q         3 &E
        1,2 5 P           4 &E
        1,2 6 Q           4 &E
        1,2 7 Q&R         3 &E
        1,2 8 Q           7 &E
        1,2 9 R           7 &E
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
        1 3 P   1,2 &E
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) 2,1 &I
        1   4 P&Q         3 &E
        2   5 Q&R         3 &E
    """
    assert _map_is_valid(text) == [True, True, True, False, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 Q&R         P
        2     2 P&Q         P
        1,2   3 (P&Q)&(Q&R) 2,1 &I
        1,2,3 4 P&Q         3 &E
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 PvQ P
        1 2 P   1 &E
    """
    assert _map_is_valid(text) == [True, False]

    # None of the formulas are the same.
    text: str = """
        1   1 Q&R         P
        2   2 P&Q         P
        1,2 3 (P&Q)&(Q&R) 2,1 &I
        1,2 4 P&P         3 &E
    """
    assert _map_is_valid(text) == [True, True, True, False]

def test_or_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P       P
        1 2 PvQ     1 vI
        1 3 Rv(PvQ) 2 vI
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     1,2 &I
        1,2 4 Rv(P&Q) 3 vI
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
        1 2 PvQ     1 vI
        1 3 Rv(PvQ) 1,2 vI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     1,2 &I
        2   4 Rv(P&Q) 3 vI
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 PvQ 1 vI
    """
    assert _map_is_valid(text) == [True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 P   P
        1 2 P&Q 1 vI
    """
    assert _map_is_valid(text) == [True, False]

    # None of the formulas are the same.
    text: str = """
        1 1 P   P
        2 2 Q   P
        2 3 PvP 2 vI
    """
    assert _map_is_valid(text) == [True, True, False]

def test_or_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             1,2,2,2,2 vE
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             1,2,2,2 vE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             1,2,2,2,2,2 vE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        - 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R&P) P
        2   2 P&Q         A
        2   3 P           2 &E
        4   4 R&P         A
        4   5 P           4 &E
        1,2 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)&(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Second rule line is not assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         P
        2 3 P           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # First assumption is incorrect.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&P         A
        2 3 P           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Third rule line does not depend on the first assumption.
    text: str = """
        1   1 (P&Q)v(R&P) P
        2   2 P&Q         A
        3   3 P           A
        4   4 R&P         A
        4   5 P           4 &E
        1,3 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Third rule line is not the same as the result.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 Q           2 &E
        4 4 R&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line is not assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 R&P         P
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Second assumption is incorrect.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 P&P         A
        4 5 P           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line does not depend on the first assumption.
    text: str = """
        1   1 (P&Q)v(R&P) P
        2   2 P&Q         A
        2   3 P           2 &E
        4   4 R&P         A
        5   5 P           A
        1,5 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line is not the same as the result.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           2 &E
        4 4 R&P         A
        4 5 R           4 &E
        1 6 P           1,2,3,4,5 vE
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

def test_conditional_proof_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P   A
        - 2 P>P 1,1 CP
    """
    assert _map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1   1 P       A
        2   2 Q       A
        1,2 3 P&Q     1,2 &I
        1,2 4 P       3 &E
        1   5 Q>P     2,4 CP
        -   6 P>(Q>P) 1,5 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q>P 2 CP
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q>P 2,3,4 CP
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Not discharging the premise dependency.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1,2 5 Q>P 2,4 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Incorrect connective.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q&P 2,4 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Antecedent is not an assumption.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q>P 2,4 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Consequent does not depend on the antecedent.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q>P 2,1 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Antecedent is not the same as the first rule line.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 R>P 2,4 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Consequent is not the same as the second rule line.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q 1,2 &I
        1,2 4 P   3 &E
        1   5 Q>R 2,4 CP
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

def test_modus_ponens_rule():
    # Valid use of the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 Q   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 Q   1 MP
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        3   3 Q   P
        1,2 4 Q   1,2,3 MP
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 P>Q P
        2 2 P   P
        1 3 Q   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        3   3 Q   P
        1,3 4 Q   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Incorrect connective.
    text: str = """
        1   1 P&Q P
        2   2 P   P
        1,2 3 Q   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, False]

    # Antecedent is not the same as the first rule line.
    text: str = """
        1   1 P>Q P
        2   2 Q   P
        1,2 3 Q   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, False]

    # Consequent is not the same as the first rule line.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 P   1,2 MP
    """
    assert _map_is_valid(text) == [True, True, False]

def test_double_negation_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        1 2 ~(~((P&Q)v(R>S))) 1 DNI
    """
    assert _map_is_valid(text) == [True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        1 2 ~(~((P&Q)v(R>S))) DNI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        2 2 (P&Q)v(R>S)       P
        1 3 ~(~((P&Q)v(R>S))) 1,2 DNI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        2 2 P                 P
        2 3 ~(~((P&Q)v(R>S))) 1 DNI
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R>S)       P
        2   2 P                 P
        1,2 3 ~(~((P&Q)v(R>S))) 1 DNI
    """
    assert _map_is_valid(text) == [True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)v(R>S) P
        1 2 (P&Q)v(R>S) 1 DNI
    """
    assert _map_is_valid(text) == [True, False]

    # Incorrect inner connective.
    text: str = """
        1 1 (P&Q)v(R>S)    P
        1 2 ~((P&Q)v(R>S)) 1 DNI
    """
    assert _map_is_valid(text) == [True, False]

    # Inner formula is not the same as the first rule line.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        1 2 ~(~((P&P)v(R>S))) 1 DNI
    """
    assert _map_is_valid(text) == [True, False]

def test_double_negation_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        1 2 (P&Q)v(R>S)       1 DNE
    """
    assert _map_is_valid(text) == [True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        1 2 (P&Q)v(R>S)       DNE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        2 2 ~(~((P&Q)v(R>S))) P
        1 3 (P&Q)v(R>S)       1,2 DNE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        2 2 P                 P
        2 3 (P&Q)v(R>S)       1 DNE
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 ~(~((P&Q)v(R>S))) P
        2   2 P                 P
        1,2 3 (P&Q)v(R>S)       1 DNE
    """
    assert _map_is_valid(text) == [True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)v(R>S) P
        1 2 (P&Q)v(R>S) 1 DNE
    """
    assert _map_is_valid(text) == [True, False]

    # Incorrect inner connective.
    text: str = """
        1 1 ~((P&Q)v(R>S)) P
        1 2 (P&Q)v(R>S)    1 DNE
    """
    assert _map_is_valid(text) == [True, False]

    # Inner formula is not the same as the result.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        1 2 (P&P)v(R>S)       1 DNE
    """
    assert _map_is_valid(text) == [True, False]

def test_modus_tollens_rule():
    # Valid use of the rule.
    text: str = """
        1   1 P>Q P
        2   2 ~Q  P
        1,2 3 ~P  1,2 MT
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 ~(R&S)      P
        1,2 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 ~Q  P
        1,2 3 ~P  1 MT
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 ~Q  P
        3   3 ~Q  P
        1,2 3 ~P  1,2,3 MT
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)>(R&S) P
        2 2 ~(R&S)      P
        1 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 (P&Q)>(R&S) P
        2     2 ~(R&S)      P
        3     3 ~(R&S)      P
        1,2,3 4 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Incorrect connective.
    text: str = """
        1   1 (P&Q)&(R&S) P
        2   2 ~(R&S)      P
        1,2 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

    # Second rule line is not negation.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 R&S         P
        1,2 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

    # Result is not negation.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 ~(R&S)      P
        1,2 3 P&Q         1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

    # Second rule line is not the negation of the consequent.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 ~(R&R)      P
        1,2 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

    # Result is not the negation of the antecedent.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 ~(R&S)      P
        1,2 3 ~(P&P)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, False]

def test_reductio_ad_absurdum_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P&(~P)    A
        - 2 ~(P&(~P)) 1,1 RAA
    """
    assert _map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        1   5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 (P&Q)>(R&S) P
        2   2 ~(R&S)      P
        1,2 3 ~(P&Q)      1,2 MT
    """
    assert _map_is_valid(text) == [True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 P&(~P)    A
        - 2 ~(P&(~P)) 1 RAA
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 P&(~P)    A
        - 2 ~(P&(~P)) 1,1,1 RAA
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        -   5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Missing dependency number.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        1,2 5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # First rule line is not assumption.
    text: str = """
        1   1 P>(~P) P
        2   2 P      P
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        1   5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Contradiction does not depend on the assumption.
    text: str = """
        1 1 Q      A
        2 2 P&(~P) P
        2 3 ~Q     1,2 RAA
    """
    assert _map_is_valid(text) == [True, True, False]

    # Contradiction has incorrect connective.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 Pv(~P) 3 vI
        1   5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Contradiction is not in the correct format.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 (~P)&P 3,2 &I
        1   5 ~P     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Contradiction is not in the correct format.
    text: str = """
        1   1 P>(~P)    P
        2   2 P         A
        1,2 3 ~P        1,2 MP
        1,2 4 (~P)&(~P) 3,3 &I
        1   5 ~P        2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Result is not a negation.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        1   5 P      2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Result is not the negation of the assumption.
    text: str = """
        1   1 P>(~P) P
        2   2 P      A
        1,2 3 ~P     1,2 MP
        1,2 4 P&(~P) 2,3 &I
        1   5 ~Q     2,4 RAA
    """
    assert _map_is_valid(text) == [True, True, True, True, False]
