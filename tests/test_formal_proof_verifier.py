from formal_proof_verifier import create_lines_from_text

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
