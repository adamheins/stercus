from .constants import *
from .errors import *
from .compiler import compile
from .lexer import lex
from .parser import parse
from .preprocessor import preprocess


def compile_string(src, memory_size):
    """Compile a Stercus string to C.

    Parameters
    ----------
    src : str
        String of Stercus code.
    memory_size : int
        Number of bytes to use for program memory.

    Returns
    -------
    : str
        Corresponding string of C code.
    """
    src = preprocess(src)
    src = lex(src)
    src = parse(src)
    src = compile(src, memory_size)
    return src


def compile_file(path, **kwargs):
    """Compile a Stercus file to C.

    Parameters
    ----------
    path : str or Path
        The path to the Stercus source file.
    **kwargs : dict
        Keyword arguments are passed to ``compile_string``.

    Returns
    -------
    : str
        Corresponding string of C code.
    """
    with open(path) as f:
        src = f.read()
    return compile_string(src, **kwargs)
