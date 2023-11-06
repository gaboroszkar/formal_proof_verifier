import pytest

from formal_proof_verifier.formal_proof_verifier import create_formula as cf
from formal_proof_verifier.formal_proof_verifier import Formula, FormulaType

def test_recognize_predicate():
    formula: Formula = cf("P&Predicate(variable)")
    assert formula.type == FormulaType.and_type
    assert formula.left.type == FormulaType.atomic_type
    assert formula.left.atom == "P"
    assert formula.right.type == FormulaType.predicate_type
    assert formula.right.predicate == "Predicate"
    assert formula.right.variables == ["variable"]

    formula: Formula = cf("Pv(Predicate)something")
    assert formula.type == FormulaType.or_type
    assert formula.left.type == FormulaType.atomic_type
    assert formula.left.atom == "P"
    assert formula.right.type == FormulaType.predicate_type
    assert formula.right.predicate == "Predicate"
    assert formula.right.variables == ["something"]

    formula: Formula = cf("Tripredicate(v1,v2,v3)>P")
    assert formula.type == FormulaType.conditional_type
    assert formula.left.type == FormulaType.predicate_type
    assert formula.left.predicate == "Tripredicate"
    assert formula.left.variables == ["v1", "v2", "v3"]
    assert formula.right.type == FormulaType.atomic_type
    assert formula.right.atom == "P"

    formula: Formula = cf("(a)is(b)vP")
    assert formula.type == FormulaType.or_type
    assert formula.left.type == FormulaType.predicate_type
    assert formula.left.predicate == "is"
    assert formula.left.variables == ["a", "b"]
    assert formula.right.type == FormulaType.atomic_type
    assert formula.right.atom == "P"

    formula: Formula = cf("(~(S={}))>(Ex(x)in(S))")
    assert formula.type == FormulaType.conditional_type
    assert formula.left.type == FormulaType.not_type
    assert formula.left.inner.type == FormulaType.predicate_type
    assert formula.left.inner.predicate == "="
    assert formula.left.inner.variables == ["S", "{}"]
    assert formula.right.type == FormulaType.existential_type
    assert formula.right.variable == "x"
    assert formula.right.inner.type == FormulaType.predicate_type
    assert formula.right.inner.predicate == "in"
    assert formula.right.inner.variables == ["x", "S"]

def test_formula_comparison():
    assert cf("P") == cf("P")
    assert cf("P&Q") == cf("P&Q")
    assert cf("PvQ") == cf("PvQ")
    assert cf("P>Q") == cf("P>Q")
    assert cf("~P") == cf("~P")
    assert cf("F(a,b,c)") == cf("F(a,b,c)")
    assert cf("Ax(P&F(a,x))") == cf("Ay(P&F(a,y))")
    assert cf("Ex(F(x,b)vQ)") == cf("Ey(F(y,b)vQ)")

    assert cf("P") != cf("Q")
    assert cf("P&Q") != cf("PvQ")
    assert cf("P>Q") != cf("PvQ")
    assert cf("~P") != cf("P")
    assert cf("F(a,b,c)") != cf("G(a,b,c)")
    assert cf("F(a,b,c)") != cf("F(a,b)")
    assert cf("F(a,b,c)") != cf("F(a,b,d)")
    assert cf("Ex(F(x))") != cf("Ay(F(y))")

    assert cf("P&Q") != cf("R&Q")
    assert cf("PvQ") != cf("PvR")
    assert cf("~P") != cf("~Q")

    assert cf("Ax(P&F(a,x))") != cf("Ay(P&F(a,x))")
    assert cf("Ex(F(x,b)vQ)") != cf("Ey(F(x,b)vQ)")
