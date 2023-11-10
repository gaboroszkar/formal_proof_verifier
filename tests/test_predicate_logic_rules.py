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

    # Variable exists freely among the dependencies in the left formula.
    text: str = """
        1 1 Ax(F(a)&G(x)) P
        1 2 F(a)&G(b)     1 UE
        1 3 F(a)          2 &E
        1 4 Ax(F(x))      3 UI
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Variable exists freely among the dependencies in the right formula.
    text: str = """
        1 1 Ax(F(x)&G(a)) P
        1 2 F(b)&G(a)     1 UE
        1 3 G(a)          2 &E
        1 4 Ax(G(x))      3 UI
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Variable exists freely among the dependencies in the inner formula.
    text: str = """
        1   1 Ax(F(a))      P
        2   2 Ax(G(x))      P
        1   3 F(a)          1 UE
        2   4 G(a)          2 UE
        1,2 5 F(a)&G(a)     3,4 &I
        1,2 6 Ax(F(x)&G(x)) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, False]

    # Variable exists among the dependencies in the inner formula.
    text: str = """
        1 1 Ax(Ay(F(x))) P
        1 2 Az(F(z))     1 UE
        1 3 F(y)         2 UE
        1 4 Az(F(z))     3 UI
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Formula from which we generalize is very similar,
    # there is a corresponding variable because of this similarity,
    # but the formulas are not exactly the same.
    text: str = """
        1 1 Ax(F(x)) P
        1 2 F(a)     1 UE
        1 3 Ax(G(x)) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]

    # Formula from which we generalize is very similar,
    # there is a corresponding variable because of this similarity,
    # but the formulas are not exactly the same.
    text: str = """
        1 1 Ax(F(x)&(Ey(G(y)))) P
        1 2 F(a)&(Ey(G(y)))     1 UE
        1 3 Ax(F(x)&(Ay(G(y)))) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]

    # Formula from which we generalize is very similar,
    # there is a corresponding variable because of this similarity,
    # but the formulas are not exactly the same.
    text: str = """
        1 1 Ax(F(x,b)) P
        1 2 F(a,b)     1 UE
        1 3 Ax(F(x,c)) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]

    # Formula from which we generalize is very similar,
    # there is a corresponding variable because of this similarity,
    # but the formulas are not exactly the same.
    text: str = """
        1 1 Ax(F(x)&G(x)) P
        1 2 F(a)&G(a)     1 UE
        1 3 F(a)          2 &E
        1 4 F(b)&G(b)     1 UE
        1 5 G(b)          4 &E
        1 6 F(a)&G(b)     3,5 &I
        1 7 Ax(F(x)&G(x)) 6 UI
    """
    assert map_is_valid(text) == [True, True, True, True, True, True, False]

    # Cannot find corresponding variable because
    # the predicate has different number of variables.
    text: str = """
        1 1 Ax(P&F(x,y))   P
        1 2 P&F(a,y)       1 UE
        1 3 Ax(P&F(a,y,z)) 2 UI
    """
    assert map_is_valid(text) == [True, True, False]

def test_universal_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 Ax(F(x)) P
        1 2 F(a)     1 UE
    """
    assert map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ax(~(Ey(R(x,y))))&F(x) P
        1 2 (~(Ey(R(a,y))))&F(a)   1 UE
    """
    assert map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ax(P&F(x)) P
        1 2 P&F(a)     1 UE
    """
    assert map_is_valid(text) == [True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 Ax(P) P
        1 2 P     UE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 Ax(P) P
        2 2 Ax(Q) P
        1 3 P     1,2 UE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     1,2 &I
        1,2 4 Ax(P&Q) 3 UI
        2   5 P&Q     4 UE
    """
    assert map_is_valid(text) == [True, True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 Ax(P) P
        2   2 Ax(Q) P
        1,2 3 Q     2 UE
    """
    assert map_is_valid(text) == [True, True, False]

    # Formulas are not the same because
    # the connectives are different.
    text: str = """
        1 1 Ax(P&F(x,y)) P
        1 2 PvF(a,y)     1 UE
    """
    assert map_is_valid(text) == [True, False]

    # Invalid quantifier.
    text: str = """
        1 1 Ex(P&F(x)) P
        1 2 P&F(a)     1 UE
    """
    assert map_is_valid(text) == [True, False]

    # Formulas are not the same because
    # the bound variables are different.
    text: str = """
        1 1 Ax(Ey(F(x,y))) P
        1 2 Ey(F(a,b))     1 UE
    """
    assert map_is_valid(text) == [True, False]

    # Cannot find corresponding variable,
    # and the formulas are not the same.
    text: str = """
        1 1 Ax(P&F(a,b)) P
        1 2 P&F(c,d)     1 UE
    """
    assert map_is_valid(text) == [True, False]

    # Cannot find corresponding variable because
    # the predicate has different number of variables.
    text: str = """
        1 1 Ax(P&F(x,y,z)) P
        1 2 P&F(a,y)       1 UE
    """
    assert map_is_valid(text) == [True, False]

def test_existential_introduction_rule():
    # Valid use of the rule.
    text: str = """
        1 1 F(a)     P
        1 2 Ex(F(x)) 1 EI
    """
    assert map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1 1 (~(Ey(R(a,y))))&F(a)   P
        1 2 Ex(~(Ey(R(x,y))))&F(x) 1 EI
    """
    assert map_is_valid(text) == [True, True]

    # Valid use of the rule.
    text: str = """
        1 1 P&F(a)     P
        1 2 Ex(P&F(x)) 1 EI
    """
    assert map_is_valid(text) == [True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 P     P
        1 2 Ex(P) EI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 P     P
        2 2 Q     P
        1 3 Ex(P) 1,2 EI
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 P&Q     1,2 &I
        2   4 Ex(P&Q) 3 EI
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 P       P
        2   2 Q       P
        1,2 3 Ex(P&Q) 1 EI
    """
    assert map_is_valid(text) == [True, True, False]

    # Incorrect quantifier.
    text: str = """
        1 1 F(a)     P
        1 2 Ax(F(x)) 1 EI
    """
    assert map_is_valid(text) == [True, False]

    # Formulas are not the same because
    # the connectives are different.
    text: str = """
        1 1 PvF(a,y)     P
        1 2 Ex(P&F(x,y)) 1 EI
    """
    assert map_is_valid(text) == [True, False]

    # Formulas are not the same because
    # the bound variables are different.
    text: str = """
        1 1 Ay(F(a,b))     P
        1 2 Ex(Ay(F(x,y))) 1 EI
    """
    assert map_is_valid(text) == [True, False]

    # Cannot find corresponding variable,
    # and the formulas are not the same.
    text: str = """
        1 1 P&F(c,d)     P
        1 2 Ex(P&F(a,b)) 1 EI
    """
    assert map_is_valid(text) == [True, False]

    # Cannot find corresponding variable because
    # the predicate has different number of variables.
    text: str = """
        1 1 P&F(a,y)       P
        1 2 Ex(P&F(x,y,z)) 1 EI
    """
    assert map_is_valid(text) == [True, False]

def test_existential_elimination_rule():
    # Valid use of the rule.
    text: str = """
        1 1 Ex(P) P
        2 2 P     A
        2 3 PvQ   2 vI
        1 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ex(F(x)&G(x)) P
        2 2 F(a)&G(a)     A
        2 3 F(a)          2 &E
        2 4 Ex(F(x))      3 EI
        1 5 Ex(F(x))      1,2,4 EE
    """
    assert map_is_valid(text) == [True, True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1 1 Ex(Ay(R(y))&(~G(x))) P
        2 2 Ay(R(y))&(~G(a))     A
        2 3 R(y)&(~G(a))         2 UE
        2 4 ~G(a)                3 &E
        2 5 Ex(~G(x))            4 EI
        1 6 Ex(~G(x))            1,2,5 EE
    """
    assert map_is_valid(text) == [True, True, True, True, True, True]

    # Valid use of the rule.
    text: str = """
        1    1 Ex(F(x)&G(x))        P
        2    2 Ax(F(x)>(G(x)>H(x))) P
        3    3 F(a)&G(a)            A
        3    4 F(a)                 3 &E
        3    5 G(a)                 3 &E
        2    6 F(a)>(G(a)>H(a))     2 UE
        2,3  7 G(a)>H(a)            6,4 MP
        2,3  8 H(a)                 7,5 MP
        2,3  9 Ex(H(x))             8 EI
        1,2 10 Ex(H(x))             1,3,9 EE
    """
    assert map_is_valid(text) == [True, True, True, True, True, True, True, True, True, True]

    # Missing line numbers for the rule.
    text: str = """
        1 1 Ex(P) P
        2 2 P     A
        2 3 PvQ   2 vI
        1 4 PvQ   2,3 EE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 Ex(P)   P
        2 2 P       A
        2 3 PvQ     2 vI
        2 4 (PvQ)vR 3 vI
        1 5 (PvQ)vR 1,2,3,4 EE
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Missing dependency number.
    text: str = """
        1 1 Ex(P) P
        2 2 P     A
        2 3 PvQ   2 vI
        - 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Extra invalid dependency number.
    text: str = """
        1   1 Ex(P) P
        2   2 P     A
        2   3 PvQ   2 vI
        1,2 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Incorrect quantifier.
    text: str = """
        1 1 Ax(P) P
        2 2 P     A
        2 3 PvQ   2 vI
        1 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # Second rule line is not an assumption.
    text: str = """
        1 1 Ex(P) P
        2 2 P     P
        2 3 PvQ   2 vI
        1 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # There is no corresponding variable,
    # and the existential formula and
    # the typical disjunct is not the same.
    text: str = """
        1 1 Ex(P) P
        2 2 Q     A
        2 3 PvQ   2 vI
        1 4 PvQ   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # There is no corresponding variable because
    # the number of variables in the predicate is different,
    # and the existential formula and
    # the typical disjunct is not the same.
    text: str = """
        1 1 Ex(F(x,y,z)) P
        2 2 F(a,y)       A
        2 3 Ex(F(x,y))   2 EI
        1 4 Ex(F(x,y))   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # There is no corresponding variable,
    # the existential formula and
    # the typical disjunct is not the same
    # because the free variables are different.
    text: str = """
        1 1 Ex(F(d,b,c)) P
        2 2 F(a,b,c)     A
        2 3 Ex(F(a,b,c)) 2 EI
        1 4 Ex(F(a,b,c)) 1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # There is no corresponding variable,
    # the existential formula and
    # the typical disjunct is not the same
    # because the bound variables are different.
    text: str = """
        1 1 Ex(Ey(R(a,y))) P
        2 2 Ey(R(a,b))     A
        2 3 Ex(Ey(R(a,b))) 2 EI
        1 4 Ex(Ey(R(a,b))) 1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # The derived formula from the assumption,
    # and the result is not the same because the
    # connectives are different.
    text: str = """
        1 1 Ex(P) P
        2 2 P     A
        2 3 PvQ   2 vI
        1 4 P&Q   1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # The derived formula from the assumption,
    # and the result is not the same because the
    # number of variables in the predicates are different.
    text: str = """
        1 1 Ex(F(x,b))   P
        2 2 F(a,b)       A
        2 3 F(a,b)vP     2 vI
        2 4 Ex(F(x,b)vP) 3 EI
        1 5 Ex(F(x)vP)   1,2,4 EE
    """
    assert map_is_valid(text) == [True, True, True, True, False]

    # The derived formula from the assumption,
    # and the result is not the same because the
    # free variables are different.
    text: str = """
        1 1 Ex(F(x,b,c)) P
        2 2 F(a,b,c)     A
        2 3 Ex(F(x,b,c)) 2 EI
        1 4 Ex(F(x,b,d)) 1,2,3 EE
    """
    assert map_is_valid(text) == [True, True, True, False]

    # The derived formula from the assumption,
    # and the result is not the same because the
    # bound variables are different.
    text: str = """
        1 1 Ex(F(x,b))     P
        2 2 F(a,b)         A
        2 3 Ey(F(a,y))     2 EI
        2 4 Ex(Ey(F(x,y))) 3 EI
        1 5 Ex(Ey(F(x,b))) 1,2,4 EE
    """
    assert map_is_valid(text) == [True, True, True, True, False]
