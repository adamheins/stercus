import subprocess
import tempfile

import stercus


MEMORY_SIZE = 100


def _compile_and_run(app_table, args=None, input=None):
    """Compile stercus -> C -> binary and run."""
    if args is None:
        args = []

    with tempfile.TemporaryDirectory() as tmpdir:
        c_src = stercus.compile(app_table, MEMORY_SIZE)
        c_file = tmpdir + "/test.c"
        with open(c_file, "w") as f:
            f.write(c_src)

        out_file = tmpdir + "/test.out"
        subprocess.run(["gcc", c_file, "-o", out_file])
        return subprocess.run(
            [out_file] + args,
            input=input,
            capture_output=True,
            encoding="utf-8",
        )


def test_compile_empty():
    app_table = {"main": []}
    out = _compile_and_run(app_table, args=["foo"])
    assert out.stdout == ""


def test_compile_increment():
    app_table = {"main": ["[", "0", "+", ".", "]"]}
    out = _compile_and_run(app_table)
    assert out.stdout == "1"


def test_compile_decrement():
    app_table = {"main": ["[", "0", "-", ".", "]"]}
    out = _compile_and_run(app_table)
    assert out.stdout == "-1"


def test_compile_assignment():
    app_table = {"main": ["[", "0", "13", ".", "]"]}
    out = _compile_and_run(app_table)
    assert out.stdout == "13"


def test_compile_echo():
    app_table = {"main": ["[", "0", ":", "]"]}
    out = _compile_and_run(app_table, args=["a"])
    assert out.stdout == "a"


def test_compile_input():
    app_table = {"main": ["[", "0", ",", ":", "]"]}
    out = _compile_and_run(app_table, input="a")
    assert out.stdout == "a"


def test_compile_assign_from_variable():
    val = "5"
    # assign byte 0 to val then assign byte 1 to the value of byte 1
    app_table = {
        "main": ["[", "0", val, ".", "]", "[", "1", "[", "0", "]", ".", "]"]
    }
    out = _compile_and_run(app_table)
    assert out.stdout[0] == out.stdout[1] == val


def test_compile_simple_conditional():
    # no output because [0] == 0, so conditional does not execute
    app_table = {"main": ["(", "0", "[", "0", ".", "]", ")"]}
    out = _compile_and_run(app_table)
    assert out.stdout == ""


def test_compile_loop_conditional():
    main = list("[01](0[0-.])")
    app_table = {"main": main}
    out = _compile_and_run(app_table)
    assert out.stdout == "0"


def test_compile_single_custom_application():
    app_table = {
        "inc": ["[", stercus.C_FUNC_ARG_NAME, "+", "]"],
        "main": ["[", "0", "inc", ".", "]"],
    }
    out = _compile_and_run(app_table)
    assert out.stdout == "1"


def test_compile_multiple_custom_application():
    app_table = {
        "dec": ["[", stercus.C_FUNC_ARG_NAME, "-", "]"],
        "inc": ["[", stercus.C_FUNC_ARG_NAME, "+", "]"],
        "main": ["[", "0", "inc", "dec", ".", "]"],
    }
    out = _compile_and_run(app_table)
    assert out.stdout == "0"


def test_compile_multiple_custom_applications_with_ref():
    # main calls foo calls inc
    app_table = {
        "inc": ["[", stercus.C_FUNC_ARG_NAME, "+", "]"],
        "foo": ["[", stercus.C_FUNC_ARG_NAME, "inc", "]"],
        "main": ["[", "0", "foo", ".", "]"],
    }
    out = _compile_and_run(app_table)
    assert out.stdout == "1"
