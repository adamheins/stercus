import stercus


def test_preprocess_comment_line():
    program = "# This is a simple comment."
    expected = ""
    assert stercus.preprocess(program) == expected


def test_preprocess_comment_end_of_line():
    program = "[0 1] # Comment following code."
    expected = "[0 1]"
    assert stercus.preprocess(program) == expected
