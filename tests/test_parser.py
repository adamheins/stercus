import pytest
import stercus


def test_parse_applicator():
    # [0 1]
    tokens = ["[", "0", "1", "]"]
    expected = {"main": ["[", "0", "1", "]"]}
    assert stercus.parse(tokens) == expected


def test_parse_multi_applicator():
    # [0 + + +]
    tokens = ["[", "0", "+", "+", "+", "]"]
    expected = {"main": ["[", "0", "+", "+", "+", "]"]}
    assert stercus.parse(tokens) == expected


def test_parse_conditional():
    # (0 [1 +])
    tokens = ["(", "0", "[", "1", "+", "]", ")"]
    expected = {"main": ["(", "0", "[", "1", "+", "]", ")"]}
    assert stercus.parse(tokens) == expected


def test_parse_nested_conditional():
    # (0 (1))
    tokens = ["(", "0", "(", "1", ")", ")"]
    expected = {"main": ["(", "0", "(", "1", ")", ")"]}
    assert stercus.parse(tokens) == expected


def test_parse_custom_application():
    # {a [$ +]}
    # [0 a]
    tokens = ["{", "a", "[", "$", "+", "]", "}", "[", "0", "a", "]"]
    expected = {
        "a": ["[", "s0", "+", "]"],
        "main": ["[", "0", "a", "]"],
    }
    assert stercus.parse(tokens) == expected


def test_parse_custom_application_named_main():
    # {main [$ +]}
    tokens = ["{", "main", "[", "$", "+", "]", "}"]
    with pytest.raises(stercus.ApplicationNameError):
        stercus.parse(tokens)


def test_parse_custom_application_starts_with_num():
    # {1 [$ +]}
    tokens = ["{", "1", "[", "$", "+", "]", "}"]
    with pytest.raises(stercus.ApplicationNameError):
        stercus.parse(tokens)


def test_parse_custom_application_nested():
    # {outer
    #   {inner [$ +]}
    # [$ inner]}
    tokens = [
        "{",
        "outer",
        "{",
        "inner",
        "[",
        "$",
        "+",
        "]",
        "}",
        "[",
        "$",
        "inner",
        "]",
        "}",
    ]
    with pytest.raises(stercus.UnbalancedBracketsError):
        stercus.parse(tokens)
