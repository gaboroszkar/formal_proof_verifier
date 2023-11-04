from formal_proof_verifier import create_lines_from_text

def test_multiple_reductio_ad_absurdum():
    text: str = """
        1         1 (P&Q)>R                        P
        2         2 ~((P>R)v(Q>R))                 A
        3         3 P                              A
        4         4 Q                              A
        3,4       5 P&Q                            &I 3,4
        1,3,4     6 R                              MP 1,5
        1,4       7 P>R                            CP 3,6
        1,4       8 (P>R)v(Q>R)                    vI 7
        1,2,4     9 ((P>R)v(Q>R))&(~((P>R)v(Q>R))) &I 8,2
        1,2      10 ~Q                             RAA 4,9
        1,2,4    11 Q&(~Q)                         &I 4,10
        12       12 ~R                             A
        1,2,4,12 13 (Q&(~Q))&(~R)                  &I 11,12
        1,2,4,12 14 Q&(~Q)                         &E 13
        1,2,4    15 ~(~R)                          RAA 12,14
        1,2,4    16 R                              DNE 15
        1,2      17 Q>R                            CP 4,16
        1,2      18 (P>R)v(Q>R)                    vI 17
        1,2      19 ((P>R)v(Q>R))&(~((P>R)v(Q>R))) &I 18,2
        1        20 ~(~((P>R)v(Q>R)))              RAA 2,19
        1        21 (P>R)v(Q>R)                    DNE 20
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)

def test_principle_of_explosion_with_modus_tollens():
    text: str = """
        1    1 P&(~P)     A
        2    2 ~Q         A
        1    3 P          &E 1
        1,2  4 P&(~Q)     &I 3,2
        1,2  5 P          &E 4
        1    6 (~Q)>P     CP 2,5
        1    7 ~P         &E 1
        1    8 ~(~Q)      MT 6,7
        1    9 Q          DNE 8
        -   10 (P&(~P))>Q CP 1,9
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)

def test_reductio_ad_absurdum_with_modus_tollens():
    text: str = """
        1    1 P>(Q&(~Q))        A
        2    2 P                 A
        3    3 (P>P)             A
        2,3  4 P&(P>P)           &I 2,3
        2,3  5 P                 &E 4
        2    6 (P>P)>P           CP 3,5
        1,2  7 Q&(~Q)            MP 1,2
        1,2  8 Q                 &E 7
        1    9 P>Q               CP 2,8
        1,2 10 ~Q                &E 7
        1,2 11 ~P                MT 9,10
        1,2 12 ~(P>P)            MT 6,11
        1   13 P>(~(P>P))        CP 2,12
        -   14 P>P               CP 2,2
        -   15 ~(~(P>P))         DNI 14
        1   16 ~P                MT 13,15
        -   17 (P>(Q&(~Q)))>(~P) CP 1,16
    """

    lines: List[Union[str, Line]] = create_lines_from_text(text)

    assert all(line[1].is_valid() for line in lines)
