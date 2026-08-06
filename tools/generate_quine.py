#!/usr/bin/env python3
"""
Stercus quine generator (written by Claude Opus 5)

Writes a self-reproducing Stercus program to examples/quine.cus.

How it works
------------

The source is two parts:

    S = D + P

D is the *data* section: a run of literal assignments

    [1 c1][2 c2]...[cN N]

where ci is the ASCII code of the i-th character of P (the *printer*).
Note that D encodes P only -- it does not encode itself.  Running D just
fills cells 1..N; it produces no output.

P is the *printer*, and is made of two loops over those same cells.  Both
walk a pointer (cell PTR) up from 1 and stop at the first zero cell, which
is cell N+1: calloc zeroes memory and nothing else is ever written there.

  Loop 1 reproduces D.  For each cell it prints '[', the index as an int,
  a space, the value as an int, and ']' -- exactly the text of the
  assignment that stored it:

      [PTR 1]([PTR][0 91 :][PTR .][0 32 :][[PTR] .][0 93 :][PTR +])

  Loop 2 reproduces P.  For each cell it prints the value as a char,
  spelling out P, because P's characters are what D stored:

      [PTR 1]([PTR][[PTR] :][PTR +])

So the output is D + P = S.  This is the usual quine trick: the data is
printed twice, once quoted (as int codes) and once plain (as characters).

A note on the conditionals: the compiler emits the loop test from the
*first* applicator in a conditional body, using the accessor twice --
`([PTR] ...)` compiles to `if(!get(get(PTR))) break;`, i.e. "test the cell
the pointer points at".  That is why each loop body opens with a bare
`[PTR]`.

There is no fixed point to solve.  P is a constant string, and D is a pure
function of P, so the program is built in one pass.

Sizing
------
PTR must sit outside the data region 1..N, and N is just len(P).  With
PTR = 200 we get N = 91, comfortably clear of the pointer.  N < 127 also
means every value stored -- indices and ASCII codes alike -- fits in a
signed char, so the quine compiles with the default cell type.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# The printer
# ---------------------------------------------------------------------------

SCRATCH = 0    # holds literal characters just long enough to print them
PTR = 200      # walking pointer; must exceed N = len(PRINTER)

PRINT_D = (
    f"[{PTR} 1]"                 # start at the first data cell
    f"([{PTR}]"                  # loop while the pointed-at cell is non-zero
    f"[{SCRATCH} 91 :]"          # '['
    f"[{PTR} .]"                 # the index
    f"[{SCRATCH} 32 :]"          # ' '
    f"[[{PTR}] .]"               # the value, as an int
    f"[{SCRATCH} 93 :]"          # ']'
    f"[{PTR} +]"
    f")"
)

PRINT_P = (
    f"[{PTR} 1]"
    f"([{PTR}]"
    f"[[{PTR}] :]"               # the value, as a char
    f"[{PTR} +]"
    f")"
)

PRINTER = PRINT_D + PRINT_P


def data_section(text):
    """Return the assignments that store *text* into cells 1..len(text)."""
    return "".join(f"[{i} {ord(c)}]" for i, c in enumerate(text, start=1))


def build_quine():
    src = data_section(PRINTER) + PRINTER
    n = len(PRINTER)
    if n >= PTR:
        raise RuntimeError(f"printer ({n} chars) overruns pointer cell {PTR}")
    return src


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def simulate(src):
    """Interpret the quine directly and return what it writes to stdout."""
    mem = {}
    body = src[: src.index(PRINTER)]
    pos = 0
    while pos < len(body):
        assert body[pos] == "[", f"expected '[' at {pos}"
        close = body.index("]", pos)
        index, value = body[pos + 1 : close].split()
        mem[int(index)] = int(value)
        pos = close + 1

    out = []
    ptr = 1
    while mem.get(ptr, 0) != 0:
        out.append(f"[{ptr} {mem[ptr]}]")
        ptr += 1
    ptr = 1
    while mem.get(ptr, 0) != 0:
        out.append(chr(mem[ptr]))
        ptr += 1
    return "".join(out)


def report_mismatch(got, want):
    print(f"  got {len(got)} chars, want {len(want)}", file=sys.stderr)
    for i, (a, b) in enumerate(zip(got, want)):
        if a != b:
            print(f"  first difference at char {i}", file=sys.stderr)
            print(f"    got  {got[max(0, i - 10):i + 20]!r}", file=sys.stderr)
            print(f"    want {want[max(0, i - 10):i + 20]!r}", file=sys.stderr)
            return


def run_compiled(path, cc):
    """Compile the quine with stercusc and the C compiler, then run it."""
    root = Path(__file__).resolve().parent.parent
    binary = path.with_suffix("")
    stercusc = root / ".venv" / "bin" / "stercusc"
    if not stercusc.exists():
        stercusc = "stercusc"
    subprocess.run(
        [str(stercusc), str(path), "-c", cc, "-o", str(binary)], check=True
    )
    result = subprocess.run([str(binary)], capture_output=True, check=True)
    binary.unlink()
    return result.stdout.decode()


def main():
    parser = argparse.ArgumentParser(description="Generate a Stercus quine.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "examples" / "quine.cus",
        help="Where to write the quine.",
    )
    parser.add_argument(
        "-c",
        "--c-compiler-command",
        help="If given, also compile and run the quine to check its output.",
    )
    args = parser.parse_args()

    src = build_quine()
    print(
        f"{len(src)} chars: {len(src) - len(PRINTER)} of data"
        f" + {len(PRINTER)} of printer",
        file=sys.stderr,
    )

    output = simulate(src)
    if output != src:
        print("simulated output does not match the source", file=sys.stderr)
        report_mismatch(output, src)
        return 1
    print("simulated output matches the source", file=sys.stderr)

    args.output.write_text(src)
    print(f"wrote {args.output}", file=sys.stderr)

    if args.c_compiler_command:
        output = run_compiled(args.output, args.c_compiler_command)
        if output != src:
            print("compiled output does not match the source", file=sys.stderr)
            report_mismatch(output, src)
            return 1
        print("compiled output matches the source", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
