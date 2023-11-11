import pytest

from utils import map_is_valid
from formal_proof_verifier import create_lines_from_text

def test_equality_introduction_rule():
    # Valid use of the rule.
    text: str = """
        - 1 a=a =I
    """
    assert map_is_valid(text) == [True]

    # Too many line numbers for the rule.
    text: str = """
        - 1 a=a   =I
        - 2 b=b 1 =I
    """
    with pytest.raises(RuntimeError):
        create_lines_from_text(text)

    # Too many line numbers for the rule.
    text: str = """
        1 1 a=a =I
    """
    assert map_is_valid(text) == [False]

    # Incorrect formula type.
    text: str = """
        - 1 P&P =I
    """
    assert map_is_valid(text) == [False]

    # Incorrect predicate.
    text: str = """
        - 1 F(a,a) =I
    """
    assert map_is_valid(text) == [False]

    # Incorrect number of variables for the predicate.
    text: str = """
        - 1 =(a,a,a) =I
    """
    assert map_is_valid(text) == [False]

    # Not the same variables on both sides.
    text: str = """
        - 1 a=b =I
    """
    assert map_is_valid(text) == [False]
