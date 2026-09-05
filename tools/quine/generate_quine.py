#!/usr/bin/env python3
"""
Stercus quine generator (written by Claude Opus 5)

Writes a self-reproducing Stercus program to examples/quine.cus.

How it works
------------

The source is two parts:

    S = D + P

D is the *data* section: a run of literal assignments

    [1 c1][2 c2]...[N cN]

where ci is the ASCII code of the i-th character of P (the *printer*).
Note that D encodes P only -- it does not encode itself.  Running D just
fills cells 1..N; it produces no output.

P is the *printer*, and is made of two loops over those same cells:

    ([0 +][A :][0 .][B :][[0] .][C :])([Q +][[Q] :])

  Loop 1 reproduces D.  For each cell it prints '[', the index as an int,
  a space, the value as an int, and ']' -- exactly the text of the
  assignment that stored it.

  Loop 2 reproduces P.  For each cell it prints the value as a char,
  spelling out P, because P's characters are what D stored.

So the output is D + P = S.  This is the usual quine trick: the data is
printed twice, once quoted (as int codes) and once plain (as characters).

Three tricks keep the printer short, and the printer is what costs: every
character of P is a cell, and every cell is ~7 characters of D, so a
character shaved off P is worth about 8 off the quine.

  1. The literals come out of the data.  Printing '[', ' ' and ']' needs
     those bytes in memory somewhere, and the data section is already full
     of them -- P's own characters.  So instead of a scratch cell loaded
     on the fly (`[0 91 :]`, 8 chars) we just print the data cell that
     happens to hold that byte (`[A :]`, 5 chars).  P begins

         ( [ 0   + ]
         1 2 3 4 5 6      <- cell

     so A=2 holds '[', B=4 holds ' ' and C=6 holds ']'.  This is
     self-referential -- the indices depend on P, which depends on the
     indices -- so build_printer() iterates to a fixed point.

  2. The pointer bump rides in the loop test.  The compiler takes the
     first applicator of a conditional as its test, applying it and then
     testing the cell it points at: `([0 +] ...)` compiles to

         while(1){ set(0, get(0)+1); if(!get(get(0))) break; ... }

     which is a walk, a test and a stop condition in seven characters, and
     needs no separate `[0 +]` in the body.

  3. Neither loop needs an initializer.  Memory is calloc'd, so a pointer
     cell starts at 0 and the test above bumps it to 1 -- the first data
     cell -- before the first test.  Loop 1 uses cell 0.  Loop 2 cannot
     reuse it (loop 1 leaves it at N+1, and `[0 0]` to reset costs more
     than it saves), so it uses cell Q = N+2, which is past the data and
     therefore still zero.  Q must clear N+1 as well as N: that cell is
     the zero terminator both loops stop on, and a pointer parked there
     would hold its own non-zero index and spin forever.

Sizing
------
N = len(P) = 50, so cells 1..50 are data, 51 is the terminator and 52 is
loop 2's pointer.  Every value stored -- indices and ASCII codes alike --
is under 127, so the quine compiles with the default `char` cell type.

There is no fixed point to solve between D and P: P is a constant string
and D is a pure function of P, so the program is built in one pass once
build_printer() has settled P's self-references.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# The printer
# ---------------------------------------------------------------------------

PTR = 0        # loop 1's pointer; cell 0 is the only free single-digit cell


def printer(open_bracket, space, close_bracket, ptr2):
    """Assemble the printer from the cell indices it reads.

    *open_bracket*, *space* and *close_bracket* are the data cells holding
    the bytes '[', ' ' and ']'; *ptr2* is loop 2's pointer cell.
    """
    print_d = (
        f"("                             # loop while the pointed-at cell is
        f"[{PTR} +]"                     # non-zero, bumping the pointer first
        f"[{open_bracket} :]"            # '['
        f"[{PTR} .]"                     # the index
        f"[{space} :]"                   # ' '
        f"[[{PTR}] .]"                   # the value, as an int
        f"[{close_bracket} :]"           # ']'
        f")"
    )
    print_p = f"([{ptr2} +][[{ptr2}] :])"
    return print_d + print_p


def build_printer():
    """Solve P's self-references: it cites cells holding its own bytes."""
    guess = printer(2, 4, 6, 52)
    for _ in range(100):
        # The i-th character of P lives in cell i+1.
        settled = printer(
            guess.index("[") + 1,
            guess.index(" ") + 1,
            guess.index("]") + 1,
            len(guess) + 2,
        )
        if settled == guess:
            return settled
        guess = settled
    raise RuntimeError("printer self-references did not settle")


PRINTER = build_printer()


def data_section(text):
    """Return the assignments that store *text* into cells 1..len(text)."""
    return "".join(f"[{i} {ord(c)}]" for i, c in enumerate(text, start=1))


def build_quine():
    src = data_section(PRINTER) + PRINTER
    n = len(PRINTER)
    ptr2 = n + 2
    if max(ptr2, max(ord(c) for c in PRINTER)) > 127:
        raise RuntimeError("quine does not fit in a signed char")
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
    ptr = 0
    while True:
        ptr += 1
        if mem.get(ptr, 0) == 0:
            break
        out.append(f"[{ptr} {mem[ptr]}]")
    ptr = 0
    while True:
        ptr += 1
        if mem.get(ptr, 0) == 0:
            break
        out.append(chr(mem[ptr]))
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
    root = Path(__file__).resolve().parent.parent.parent
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
        default="quine.cus",
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
