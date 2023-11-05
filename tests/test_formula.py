import pytest

from formal_proof_verifier.formal_proof_verifier import create_formula, Formula, FormulaType

def test_recognize_predicate():
    formula: Formula = create_formula("P&Predicate(variable)")
    assert formula.type == FormulaType.and_type
    assert formula.left.type == FormulaType.atomic_type
    assert formula.left.atom == "P"
    assert formula.right.type == FormulaType.predicate_type
    assert formula.right.predicate == "Predicate"
    assert formula.right.variables == ["variable"]

    formula: Formula = create_formula("Pv(Predicate)something")
    assert formula.type == FormulaType.or_type
    assert formula.left.type == FormulaType.atomic_type
    assert formula.left.atom == "P"
    assert formula.right.type == FormulaType.predicate_type
    assert formula.right.predicate == "Predicate"
    assert formula.right.variables == ["something"]

    formula: Formula = create_formula("Tripredicate(v1,v2,v3)>P")
    assert formula.type == FormulaType.conditional_type
    assert formula.left.type == FormulaType.predicate_type
    assert formula.left.predicate == "Tripredicate"
    assert formula.left.variables == ["v1", "v2", "v3"]
    assert formula.right.type == FormulaType.atomic_type
    assert formula.right.atom == "P"

    formula: Formula = create_formula("(a)is(b)vP")
    assert formula.type == FormulaType.or_type
    assert formula.left.type == FormulaType.predicate_type
    assert formula.left.predicate == "is"
    assert formula.left.variables == ["a", "b"]
    assert formula.right.type == FormulaType.atomic_type
    assert formula.right.atom == "P"

    formula: Formula = create_formula("(~(S={}))>(Ex(x)in(S))")
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
