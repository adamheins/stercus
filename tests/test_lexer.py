import stercus


def test_lex_applicator():
    program = "[0 , .]"
    expected = ["[", "0", ",", ".", "]"]
    assert stercus.lex(program) == expected


def test_lex_conditional():
    program = "(0 [0 -])"
    expected = ["(", "0", "[", "0", "-", "]", ")"]
    assert stercus.lex(program) == expected


def test_lex_newline():
    program = "[0\n,]"
    expected = ["[", "0", ",", "]"]
    assert stercus.lex(program) == expected


def test_lex_large_numbers():
    program = "[10\n934]"
    expected = ["[", "10", "934", "]"]
    assert stercus.lex(program) == expected


def test_lex_big_whitespace():
    program = " [\t0       1 ]   "
    expected = ["[", "0", "1", "]"]
    assert stercus.lex(program) == expected


def test_lex_custom_application():
    program = "{test [$ +]} [1 a]"
    expected = ["{", "test", "[", "$", "+", "]", "}", "[", "1", "a", "]"]
    assert stercus.lex(program) == expected


def test_lex_multiple_custom_application():
    program = """{a [$ +]}
                      {b [$ -]}
                      [1 a b .]"""
    expected = [
        "{",
        "a",
        "[",
        "$",
        "+",
        "]",
        "}",
        "{",
        "b",
        "[",
        "$",
        "-",
        "]",
        "}",
        "[",
        "1",
        "a",
        "b",
        ".",
        "]",
    ]
    assert stercus.lex(program) == expected
