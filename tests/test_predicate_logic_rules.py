import pytest

from utils import map_is_valid
from formal_proof_verifier import create_lines_from_text

def test_universal_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 P     P
        1 2 Ax(P) 1 UI
    """
    assert map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ax(F(x)&G(x)) P
        1 2 F(a)&G(a)     1 UE
        1 3 F(a)          2 &E
        1 4 Ax(F(x))      3 UI
    """
    assert map_is_valid(text) == [True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1   1 Ax(Ey(F(y)))>G(x)        P
        2   2 Ax(H(x))                 P
        1   3 (Ez(F(z)))>G(a)          1 UE
        2   4 H(a)                     2 UE
        1,2 5 ((Ez(F(z)))>G(a))&H(a)   3,4 &I
        1,2 6 Ax((Ew(F(w)))>G(x))&H(x) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ax~(Ey(R(x,y))) P
        1 2 ~(Ey(R(a,y)))   1 UE
        1 3 Ax~(Ey(R(x,y))) 2 UI
    """
    assert map_is_valid(text) == [True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 P     P
        1 2 Ax(P) UI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 P     P
        1 2 Q     P
        1 3 Ax(P) 1,2 UI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 Ax(F(x))      P
        2   2 Ax(G(x))      P
        1   3 F(a)          1 UE
        2   4 G(a)          2 UE
        1,2 5 F(a)&G(a)     3,4 &I
        2   6 Ax(F(x)&G(x)) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1     1 Ax(F(x))      P
        2     2 Ax(G(x))      P
        1     3 F(a)          1 UE
        2     4 G(a)          2 UE
        1,2   5 F(a)&G(a)     3,4 &I
        1,2,3 6 Ax(F(x)&G(x)) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, False]

    # Incorrect quantifier.
    text: str = """
        1   1 Ax(F(x))      P
        2   2 Ax(G(x))      P
        1   3 F(a)          1 UE
        2   4 G(a)          2 UE
        1,2 5 F(a)&G(a)     3,4 &I
        1,2 6 Ex(F(x)&G(x)) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, False]

    # Dependency without variable, but not the same formula.
    text: str = """
        1 1 P&Q     P
        1 2 Ax(P&P) 1 UI
    """
    assert map_is_valid(text) == [True, False]

    # Dependency without variable, but not the same formula.
    text: str = """
        1 1 P&Q     P
        1 2 Ax(P&P) 1 UI
    """
    assert map_is_valid(text) == [True, False]

    # Variable exists freely among the dependencies.
    text: str = """
        1   1 Ax(F(a))      P
        2   2 Ax(G(x))      P
        1   3 F(a)          1 UE
        2   4 G(a)          2 UE
        1,2 5 F(a)&G(a)     3,4 &I
        1,2 6 Ax(F(x)&G(x)) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, False]

    # Formula from which we generalize is very similar,
    # there is a corresponding variable because of this similarity,
    # but the formulas are not exactly the same.
    text: str = """
        1 1 Ax(F(x)) P
        1 2 F(a)     1 UE
        1 3 Ax(G(x)) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]

    # Cannot find corresponding variable because
    # the predicate has different number of variables.
    text: str = """
        1 1 Ax(P&F(x,y))   P
        1 2 P&F(a,y)       1 UE
        1 3 Ax(P&F(a,y,z)) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]
