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

where ci is the ASCII code of a character of P (the *printer*).  Note that
D encodes P only -- it does not encode itself.  Running D just fills cells
1..N; it produces no output.

P is the *printer*, and is made of two loops over those same cells:

    ([0 +][7 :][0 .][4 :][[0] .][2 :])([0 -][[0] :])

  Loop 1 reproduces D.  It walks cell 0 up from 1 and, for each cell,
  prints '[', the index as an int, a space, the value as an int, and ']'
  -- exactly the text of the assignment that stored it.

  Loop 2 reproduces P.  It walks back down and prints each value as a
  char, spelling out P, because P's characters are what D stored.

So the output is D + P = S.  This is the usual quine trick: the data is
printed twice, once quoted (as int codes) and once plain (as characters).

P is stored *backwards*: cell i holds P[N - i].  Loop 2 runs backwards
too, so the two reversals cancel and P comes out forwards; see trick 3.

Keeping it short
----------------

The printer is what costs.  Every character of P is a cell, and every
cell is ~7 characters of D, so a character shaved off P is worth about 8
off the quine.  Four tricks get P down to 48 characters:

  1. The literals come out of the data.  Printing '[', ' ' and ']' needs
     those bytes in memory somewhere, and the data section is already full
     of them -- P's own characters.  So instead of a scratch cell loaded
     on the fly (`[0 91 :]`, 8 chars) we just print the data cell that
     happens to hold that byte (`[7 :]`, 5 chars).  This is
     self-referential -- the indices depend on P, which depends on the
     indices -- so build_printer() iterates to a fixed point.

  2. The pointer moves in the loop test.  The compiler takes the first
     applicator of a conditional as its test, applying it and then testing
     the cell it points at, so `([0 +] ...)` compiles to

         while(1){ set(0, get(0)+1); if(!get(get(0))) break; ... }

     -- a step, a test and a stop condition in seven characters, with no
     separate `[0 +]` needed in the body.

  3. Both loops share cell 0 as their pointer, and neither initializes it.
     Memory is calloc'd, so cell 0 starts at 0 and trick 2 bumps it to the
     first data cell before the first test.  Loop 1 leaves it at N+1, the
     zero terminator it stopped on -- which is exactly where a *descending*
     walk of the same cells has to start, so loop 2 just runs `[0 -]` and
     needs no initializer either.  Storing P backwards is what buys this:
     it lets loop 2 run backwards and still print P forwards.

     Descending also terminates for free.  When the pointer reaches 0 the
     test get(get(0)) reads cell 0 itself, finds the 0 it just wrote, and
     stops -- no terminator cell required at the bottom.

  4. Since loop 2 reads the cells last-to-first, the *tail* of P lands in
     the low-numbered cells.  P ends `[[0] :])`, which puts '[', ' ' and
     ']' in cells 7, 4 and 2 -- all single digits, so the three literal
     prints in trick 1 stay 5 characters wide instead of 6.

That is 8 applicators and 2 conditionals: 5 output applicators for loop
1's `[i v]` (27 chars, the value's `[[0] .]` needing 7 for its
indirection), 1 for loop 2 (7), 2 pointer steps (10), 4 brackets.  48.

Sizing
------
N = len(P) = 48, so cells 1..48 are data and 49 is loop 1's terminator.
Every value stored -- indices and ASCII codes alike -- is under 127, so
the quine compiles with the default `char` cell type.

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

PTR = 0    # both loops walk this cell; calloc starts it at 0, which is where
           # loop 1 wants it, and loop 1 leaves it where loop 2 wants it


def printer(open_bracket, space, close_bracket):
    """Assemble the printer from the cell indices it reads.

    *open_bracket*, *space* and *close_bracket* are the data cells holding
    the bytes '[', ' ' and ']'.
    """
    print_d = (
        f"("                        # loop while the pointed-at cell is
        f"[{PTR} +]"                # non-zero, stepping the pointer first
        f"[{open_bracket} :]"       # '['
        f"[{PTR} .]"                # the index
        f"[{space} :]"              # ' '
        f"[[{PTR}] .]"              # the value, as an int
        f"[{close_bracket} :]"      # ']'
        f")"
    )
    print_p = f"([{PTR} -][[{PTR}] :])"
    return print_d + print_p


def cell_of(text, char):
    """The lowest-numbered cell holding *char*, for a printer of *text*.

    Cell i holds text[len(text) - i], so the last occurrence of a character
    is the one sitting in the cheapest (fewest-digit) cell.
    """
    return len(text) - text.rindex(char)


def build_printer():
    """Solve P's self-references: it cites cells holding its own bytes."""
    guess = printer(7, 4, 2)
    for _ in range(100):
        settled = printer(
            cell_of(guess, "["), cell_of(guess, " "), cell_of(guess, "]")
        )
        if settled == guess:
            return settled
        guess = settled
    raise RuntimeError("printer self-references did not settle")


PRINTER = build_printer()


def data_section(text):
    """Return the assignments that store *text*, backwards, into 1..len."""
    n = len(text)
    return "".join(f"[{i} {ord(text[n - i])}]" for i in range(1, n + 1))


def build_quine():
    src = data_section(PRINTER) + PRINTER
    if max(len(PRINTER) + 1, max(ord(c) for c in PRINTER)) > 127:
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
    while True:                      # loop 1: up, printing the assignments
        ptr += 1
        if mem.get(ptr, 0) == 0:
            break
        out.append(f"[{ptr} {mem[ptr]}]")
    while True:                      # loop 2: back down, printing the chars
        ptr -= 1
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
