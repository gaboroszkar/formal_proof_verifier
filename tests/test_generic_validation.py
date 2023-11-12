from utils import map_is_valid
from formal_proof_verifier import create_lines_from_text

def test_invalid_dependency():
    text: str = """
        1    1 P&(~P)     A
        2    2 ~Q         A
        1    3 P          1 &E
        1,2  4 P&(~Q)     3,2 &I
        1,2  5 P          4 &E
        1    6 Q>(~P)     2,5 CP
        1    7 ~P         1 &E
        1    8 ~(~Q)      6,7 MT
        1    9 Q          8 DNE
        -   10 (P&(~P))>Q 1,9 CP
    """
    assert map_is_valid(text) == [True, True, True, True, True, False, True, False, False, False]

    text: str = """
        1    1 Ex(F(x)&G(x))        P
        2    2 Ax(F(x)>(G(x)>H(x))) P
        3    3 F(a)&G(a)            A
        3    4 F(a)                 3 &E
        3    5 G(b)                 3 &E
        2    6 F(a)>(G(a)>H(a))     2 UE
        2,3  7 G(a)>H(a)            6,4 MP
        2,3  8 H(a)                 7,5 MP
        2,3  9 Ex(H(x))             8 EI
        1,2 10 Ex(H(x))             1,3,9 EE
    """
    assert map_is_valid(text) == [True, True, True, True, False, True, True, False, False, False]

    text: str = """
        1   1 Ax(Ey(F(y)))>G(x)        P
        2   2 Ax(H(x))                 P
        1   3 (Ey(F(y)))>G(a)          1 UE
        2   4 H(a)                     2 UE
        1,2 5 ((Ey(F(y)))>G(a))&I(a)   3,4 &I
        1,2 6 Ax((Ey(F(y)))>G(x))&I(x) 5 UI
    """
    assert map_is_valid(text) == [True, True, True, True, False, False]

def test_multiple_reductio_ad_absurdum():
    text: str = """
        1         1 (P&Q)>R                        P
        2         2 ~((P>R)v(Q>R))                 A
        3         3 P                              A
        4         4 Q                              A
        3,4       5 P&Q                            3,4 &I
        1,3,4     6 R                              1,5 MP
        1,4       7 P>R                            3,6 CP
        1,4       8 (P>R)v(Q>R)                    7 vI
        1,2,4     9 ((P>R)v(Q>R))&(~((P>R)v(Q>R))) 8,2 &I
        1,2      10 ~Q                             4,9 RAA
        1,2,4    11 Q&(~Q)                         4,10 &I
        12       12 ~R                             A
        1,2,4,12 13 (Q&(~Q))&(~R)                  11,12 &I
        1,2,4,12 14 Q&(~Q)                         13 &E
        1,2,4    15 ~(~R)                          12,14 RAA
        1,2,4    16 R                              15 DNE
        1,2      17 Q>R                            4,16 CP
        1,2      18 (P>R)v(Q>R)                    17 vI
        1,2      19 ((P>R)v(Q>R))&(~((P>R)v(Q>R))) 18,2 &I
        1        20 ~(~((P>R)v(Q>R)))              2,19 RAA
        1        21 (P>R)v(Q>R)                    20 DNE
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)

def test_principle_of_explosion_with_modus_tollens():
    text: str = """
        1    1 P&(~P)     A
        2    2 ~Q         A
        1    3 P          1 &E
        1,2  4 P&(~Q)     3,2 &I
        1,2  5 P          4 &E
        1    6 (~Q)>P     2,5 CP
        1    7 ~P         1 &E
        1    8 ~(~Q)      6,7 MT
        1    9 Q          8 DNE
        -   10 (P&(~P))>Q 1,9 CP
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)

def test_reductio_ad_absurdum_with_modus_tollens():
    text: str = """
        1    1 P>(Q&(~Q))        A
        2    2 P                 A
        3    3 (P>P)             A
        2,3  4 P&(P>P)           2,3 &I
        2,3  5 P                 4 &E
        2    6 (P>P)>P           3,5 CP
        1,2  7 Q&(~Q)            1,2 MP
        1,2  8 Q                 7 &E
        1    9 P>Q               2,8 CP
        1,2 10 ~Q                7 &E
        1,2 11 ~P                9,10 MT
        1,2 12 ~(P>P)            6,11 MT
        1   13 P>(~(P>P))        2,12 CP
        -   14 P>P               2,2 CP
        -   15 ~(~(P>P))         14 DNI
        1   16 ~P                13,15 MT
        -   17 (P>(Q&(~Q)))>(~P) 1,16 CP
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)

def test_only_one_variable_with_property():
    text: str = """
        1         1 Ax(Ay((F(x)&F(y))>(x=y)))                    P
        2         2 ~(Ex(Ay(F(y)>(x=y))))                        A
        3         3 F(a)                                         A
        1         4 Ay((F(a)&F(y))>(a=y))                        1 UE
        1         5 (F(a)&F(b))>(a=b)                            4 UE
        6         6 F(b)                                         A
        3,6       7 F(a)&F(b)                                    3,6 &I
        1,3,6     8 a=b                                          5,7 MP
        1,3       9 F(b)>(a=b)                                   6,8 CP
        1,3      10 Ay(F(y)>(a=y))                               9 UI
        1,3      11 Ex(Ay(F(y)>(x=y)))                           10 EI
        1,2,3    12 (Ex(Ay(F(y)>(x=y))))&(~(Ex(Ay(F(y)>(x=y))))) 11,2 &I
        1,2      13 ~F(a)                                        3,12 RAA
        1,2,3    14 F(a)&(~F(a))                                 3,13 &I
        15       15 ~(b=a)                                       A
        1,2,3,15 16 (F(a)&(~F(a)))&(~(b=a))                      14,15 &I
        1,2,3,15 17 F(a)&(~F(a))                                 16 &E
        1,2,3    18 ~(~(b=a))                                    15,17 RAA
        1,2,3    19 b=a                                          18 DNE
        1,2      20 F(a)>(b=a)                                   3,19 CP
        1,2      21 Ay(F(y)>(b=y))                               20 UI
        1,2      22 Ex(Ay(F(y)>(x=y)))                           21 EI
        1,2      23 (Ex(Ay(F(y)>(x=y))))&(~(Ex(Ay(F(y)>(x=y))))) 22,2 &I
        1        24 ~(~(Ex(Ay(F(y)>(x=y)))))                     2,23 RAA
        1        25 Ex(Ay(F(y)>(x=y)))                           24 DNE
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)
