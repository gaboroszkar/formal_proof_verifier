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

    # Incorrect connective.
    text: str = """
        1 1 P   P
        1 2 P&Q vI 1
    """
    assert _map_is_valid(text) == [True, False]

    # None of the formulas are the same.
    text: str = """
        1 1 P   P
        2 2 Q   P
        2 3 PvP vI 2
    """
    assert _map_is_valid(text) == [True, True, False]

def test_or_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             vE 1,2,2,2,2
    """
    assert _map_is_valid(text) == [True, True, True]

    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             vE 1,2,2,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 ((P&Q)>R)v((P&Q)>R) P
        2 2 (P&Q)>R             A
        1 3 (P&Q)>R             vE 1,2,2,2,2,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        - 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R&P) P
        2   2 P&Q         A
        2   3 P           &E 2
        4   4 R&P         A
        4   5 P           &E 4
        1,2 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)&(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Second rule line is not assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         P
        2 3 P           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # First assumption is incorrect.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&P         A
        2 3 P           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Third rule line does not depend on the first assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        3 3 P           A
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Third rule line is not the same as the result.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 Q           &E 2
        4 4 R&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line is not assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 R&P         P
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Second assumption is incorrect.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 P&P         A
        4 5 P           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line does not depend on the first assumption.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 P           &E 2
        4 4 R&P         A
        5 5 P           A
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

    # Fourth rule line is not the same as the result.
    text: str = """
        1 1 (P&Q)v(R&P) P
        2 2 P&Q         A
        2 3 Q           &E 2
        4 4 R&P         A
        4 5 R           &E 4
        1 6 P           vE 1,2,3,4,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, False]

def test_conditional_proof_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P   A
        - 2 P>P CP 1,1
    """
    assert _map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1   1 P       A
        2   2 Q       A
        1,2 3 P&Q     &I 1,2
        1,2 4 P       &E 3
        1   5 Q>P     CP 2,4
        -   6 P>(Q>P) CP 1,5
    """
    assert _map_is_valid(text) == [True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q>P CP 2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q>P CP 2,3,4
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Not discharging the premise dependency.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1,2 5 Q>P CP 2,4
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Incorrect connective.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q&P CP 2,4
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Antecedent is not an assumption.
    text: str = """
        1   1 P   P
        2   2 Q   P
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q>P CP 2,4
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Consequent does not depend on the antecedent.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q>P CP 2,1
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Antecedent is not the same as the first rule line.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 R>P CP 2,4
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

    # Consequent is not the same as the second rule line.
    text: str = """
        1   1 P   P
        2   2 Q   A
        1,2 3 P&Q &I 1,2
        1,2 4 P   &E 3
        1   5 Q>R CP 2,4
    """
    assert _map_is_valid(text) == [True, True, True, True, False]

def test_modus_ponens_rule():
    # Valid use of the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 Q   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 Q   MP 1
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        3   3 Q   P
        1,2 4 Q   MP 1,2,3
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 P>Q P
        2 2 P   P
        1 3 Q   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        3   3 Q   P
        1,3 4 Q   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, True, False]

    # Incorrect connective.
    text: str = """
        1   1 P&Q P
        2   2 P   P
        1,2 3 Q   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, False]

    # Antecedent is not the same as the first rule line.
    text: str = """
        1   1 P>Q P
        2   2 Q   P
        1,2 3 Q   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, False]

    # Consequent is not the same as the first rule line.
    text: str = """
        1   1 P>Q P
        2   2 P   P
        1,2 3 P   MP 1,2
    """
    assert _map_is_valid(text) == [True, True, False]

def test_double_negation_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        1 2 ~(~((P&Q)v(R>S))) DNI 1
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
        1 3 ~(~((P&Q)v(R>S))) DNI 1,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        2 2 P                 P
        2 3 ~(~((P&Q)v(R>S))) DNI 1
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 (P&Q)v(R>S)       P
        2   2 P                 P
        1,2 3 ~(~((P&Q)v(R>S))) DNI 1
    """
    assert _map_is_valid(text) == [True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)v(R>S) P
        1 2 (P&Q)v(R>S) DNI 1
    """
    assert _map_is_valid(text) == [True, False]

    # Incorrect inner connective.
    text: str = """
        1 1 (P&Q)v(R>S)    P
        1 2 ~((P&Q)v(R>S)) DNI 1
    """
    assert _map_is_valid(text) == [True, False]

    # Inner formula is not the same as the first rule line.
    text: str = """
        1 1 (P&Q)v(R>S)       P
        1 2 ~(~((P&P)v(R>S))) DNI 1
    """
    assert _map_is_valid(text) == [True, False]

def test_double_negation_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        1 2 (P&Q)v(R>S)       DNE 1
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
        1 3 (P&Q)v(R>S)       DNE 1,2
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)


    # Missing dependency number.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        2 2 P                 P
        2 3 (P&Q)v(R>S)       DNE 1
    """
    assert _map_is_valid(text) == [True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 ~(~((P&Q)v(R>S))) P
        2   2 P                 P
        1,2 3 (P&Q)v(R>S)       DNE 1
    """
    assert _map_is_valid(text) == [True, True, False]

    # Incorrect connective.
    text: str = """
        1 1 (P&Q)v(R>S) P
        1 2 (P&Q)v(R>S) DNE 1
    """
    assert _map_is_valid(text) == [True, False]

    # Incorrect inner connective.
    text: str = """
        1 1 ~((P&Q)v(R>S)) P
        1 2 (P&Q)v(R>S)    DNE 1
    """
    assert _map_is_valid(text) == [True, False]

    # Inner formula is not the same as the result.
    text: str = """
        1 1 ~(~((P&Q)v(R>S))) P
        1 2 (P&P)v(R>S)       DNE 1
    """
    assert _map_is_valid(text) == [True, False]
