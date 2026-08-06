#!/usr/bin/env python3
"""
Stercus quine generator.

Produces a two-part fixed-point quine and writes it to examples/quine.cus.

Structure of the generated quine
---------------------------------

Part 1 — Data section (D):
    [1 c1][2 c2]...[N cN]

    Each cell i holds ci = the ASCII code of the i-th character of the
    complete source (D + P).  The data section produces no output.

Part 2 — Printer (P):
    A loop that reads and prints the data section, followed by a suffix
    that prints P itself one character at a time.

    Loop (uses cell 9999 as pointer, cell 0 as scratch):
        [9999 1]([[9999]][0 91 :][9999 .][0 32 :][[9999] .][0 93 :][9999 +])

    For each iteration the loop outputs:
        '[' <decimal index> ' ' <decimal value> ']'
    which exactly reproduces one [i Vi] data-cell assignment.

    Suffix:
        [0 c1 :][0 c2 :]...[0 cM :]
    where c1..cM are the ASCII codes of P (loop + suffix), printed as
    individual characters — reconstructing P verbatim.

Fixed-point computation
-----------------------
The suffix encodes P = LOOP + suffix.  We need:

    suffix = concat([0 ord(c) :] for c in LOOP + suffix)

The content of each token [0 X :] is drawn from a fixed alphabet
(['[', '0', ' ', digits, ':', ']']), so the "cost" (token length) of
encoding each character of the suffix is itself deterministic.

We solve for the suffix by direct construction:

  1. Build the suffix token-by-token, treating it as an already-known
     string being encoded.  The suffix begins empty.
  2. For each character of LOOP (known), append [0 ord(c) :].
  3. For each character of the suffix built so far (known), append
     [0 ord(c) :].  Because every character added in step 3 is a
     character from the set {[, 0, space, 1-9, :, ]}, its encoding cost
     is fixed — we can unroll the self-encoding one token at a time.
  4. Keep extending until no more characters are added.

This terminates because every character we add to the suffix we
immediately encode, and each encoding step adds a fixed number of
characters whose encoding we then also append.  The suffix grows in
discrete, predictable bursts until the "pending" queue empties.

Full source fixed point
-----------------------
Once P is fixed, we compute D = make_data(source) where source = D + P.
The length of D depends on source length (digit count of indices and
ASCII values), so we iterate that inner loop too — it converges quickly.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRATCH_CELL = 0      # used by the suffix to print individual chars
PTR_CELL     = 9999   # loop pointer; far from data cells (1..N)

# The invariant loop body.
# Prints '[<index> <value>]' for each occupied data cell.
LOOP = (
    f"[{PTR_CELL} 1]"
    f"([[{PTR_CELL}]]"
    f"[{SCRATCH_CELL} 91 :]"
    f"[{PTR_CELL} .]"
    f"[{SCRATCH_CELL} 32 :]"
    f"[[{PTR_CELL}] .]"
    f"[{SCRATCH_CELL} 93 :]"
    f"[{PTR_CELL} +]"
    f")"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def char_token(c: str) -> str:
    """Return the Stercus token that prints character c via cell 0."""
    return f"[{SCRATCH_CELL} {ord(c)} :]"


def token_chars(c: str) -> str:
    """Return the characters that make up char_token(c)."""
    return char_token(c)


def make_data_section(source: str) -> str:
    """Return the data section storing every ASCII code of *source*."""
    parts = []
    for i, ch in enumerate(source, start=1):
        parts.append(f"[{i} {ord(ch)}]")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Suffix fixed-point construction
# ---------------------------------------------------------------------------

def build_suffix() -> str:
    """
    Build the suffix that, when appended to LOOP, makes P self-printing.

    The suffix is a sequence of [0 X :] tokens encoding the characters of
    LOOP + suffix itself.  We construct it by processing a queue of
    characters that still need to be encoded:

      queue  = list(LOOP)           # characters of LOOP to encode first
      result = []                   # tokens built so far (as a flat char list)

    For each character c dequeued:
      token = "[0 ord(c) :]"
      append token to result
      extend queue with the characters of token  (they also need encoding)

    The process terminates naturally: enqueueing a token's own chars
    creates finite further work, and the alphabet is finite so the
    per-char cost is bounded.  However, this naive approach is infinite
    because every added token spawns more tokens.

    CORRECT APPROACH — recognise that the suffix encodes a *known* string
    (P = LOOP + suffix) and that string is determined by its own length
    and structure, not by recursive expansion.  We find the suffix by
    iterating on length:

      Given a candidate suffix S_k, the "correct" suffix for the printer
      LOOP + S_k is make_suffix(LOOP + S_k).  If make_suffix(LOOP + S_k)
      == S_k we are done.

    The catch from the caller's earlier attempt was that make_suffix always
    *grows* S.  But the characters of the suffix are drawn from a fixed
    small set, so their encoding costs are known constants.  We can
    therefore compute the required suffix length analytically and construct
    it in one shot.

    Let:
      L        = LOOP (fixed, known string)
      cost(c)  = len(char_token(c))   (7, 8, or 9)
      K_L      = sum(cost(c) for c in L)   — cost of encoding LOOP
      K_sfx(S) = sum(cost(c) for c in S)   — cost of encoding suffix S

    We need: len(S) = K_L + K_sfx(S)

    Since all suffix characters come from {[, 0-9, space, :, ]}, each
    with known cost, and suffix tokens have the form "[0 D :]" where D
    is 1-3 decimal digits, we can enumerate what a suffix of a given
    length looks like and compute K_sfx analytically.

    We instead use a direct unrolling approach that is guaranteed finite:
    build the suffix iteratively, processing one PENDING character at a
    time from a deque.  The key insight: we do NOT re-enqueue the tokens
    we generate — we just need to encode P, and P's characters past the
    LOOP are exactly the suffix tokens, which we emit in order.
    """
    # We build the suffix by simulating: "the suffix encodes LOOP+suffix".
    # Characters of LOOP are known upfront.
    # Characters of the suffix are the tokens we emit, in order.
    # We process them left-to-right:
    #   - Start with LOOP chars in a to-encode queue.
    #   - For each char c we pop, emit token(c) and enqueue token(c)'s chars.
    # This would be infinite.  Instead, observe that each suffix character
    # is drawn from the alphabet A = {[, 0, space, 1-9, :, ]}.
    # Every token "[0 X :]" consists of chars from A (since X <= 127 and
    # its digits are in 0-9).  So the per-char encoding cost is:
    #
    #   cost([) = len("[0 91 :]") = 8
    #   cost(0) = len("[0 48 :]") = 8
    #   cost( ) = len("[0 32 :]") = 8
    #   cost(1) = len("[0 49 :]") = 8
    #   ...digit chars all have 2-digit codes 48-57, cost 8
    #   cost(:) = len("[0 58 :]") = 8
    #   cost(]) = len("[0 93 :]") = 8
    #
    # ALL suffix characters have cost 8!  (Their ASCII codes are all 2-digit.)
    # So: len(suffix) = K_L + 8 * len(suffix)
    #     len(suffix) * (1 - 8) = K_L
    #     len(suffix) = K_L / (1 - 8)  <-- negative, impossible.
    #
    # This confirms a pure suffix-encodes-itself approach is impossible.
    # The suffix cannot encode itself — it always needs more space than it has.
    #
    # RESOLUTION: The suffix does NOT need to encode itself.  It encodes P,
    # and the data section D encodes the full source S = D + P.  The suffix
    # only encodes P (LOOP + suffix).  But we showed above this diverges.
    #
    # The only viable structure is: the suffix encodes LOOP only (the fixed
    # part), and the DATA SECTION encodes the suffix (the variable part).
    # But then the data section must encode the suffix, which encodes LOOP,
    # and the loop prints the data section.  This is a different quine design.
    #
    # See build_suffix_v2() below for the correct design.
    raise NotImplementedError("use build_quine() directly")


# ---------------------------------------------------------------------------
# Revised quine design
# ---------------------------------------------------------------------------
#
# The fundamental problem: a Stercus "suffix" that prints itself cannot
# exist because every printable-ASCII character has a 2-digit ASCII code
# (32-126), so encoding it costs 8 chars and produces 1 char — 8× expansion.
#
# CORRECT DESIGN:
#
#   The suffix encodes only LOOP (the fixed part).  The data section encodes
#   the suffix.  The loop prints the data section (which includes the suffix's
#   encoding).  This breaks the self-reference cycle.
#
#   Source = D + LOOP + SUFFIX
#   D encodes every character of (D + LOOP + SUFFIX) via [i Vi] assignments.
#   LOOP reads D and prints "[i Vi]" for each cell.     → reproduces D
#   SUFFIX is [0 X :] tokens encoding LOOP.             → reproduces LOOP
#   But who reproduces SUFFIX?  The loop does — SUFFIX's chars are in D!
#
#   Full source: S = D + LOOP + SUFFIX
#   Output of loop:   D  (printed from memory cells 1..|D|)
#   Output of SUFFIX: LOOP  (hardcoded)
#   But output is only D + LOOP, missing SUFFIX.
#
# CORRECT DESIGN (third attempt):
#
#   SUFFIX encodes LOOP + SUFFIX.  We showed this diverges.
#   What if we put the entire printer (LOOP + SUFFIX) into the data section?
#
#   Source = D + LOOP + SUFFIX
#   D stores ASCII codes of (D + LOOP + SUFFIX).
#   LOOP reads D and outputs all of D+LOOP+SUFFIX.
#   LOOP's output = D + LOOP + SUFFIX = full source.  ✓
#   SUFFIX is then only needed to print... nothing?  No, SUFFIX is needed
#   because LOOP stops as soon as it hits a cell with value 0.
#   If D stores the whole source, LOOP prints the whole source.
#   SUFFIX can be empty!
#
#   But wait — LOOP itself terminates when mem[ptr] == 0.  If D stores
#   the ASCII codes of the entire source S = D+LOOP, and the last cell of D
#   is followed by uninitialised (zero) cells, LOOP will stop after printing D.
#   It won't print LOOP itself unless LOOP's chars are also in D.
#
#   If D encodes S = D + LOOP (no suffix), then:
#     - N = |S| = |D| + |LOOP|
#     - D = [1 c1][2 c2]...[N cN]  where ci = ord(S[i-1])
#     - LOOP reads cells 1..N and prints S.  Output = S.  ✓
#
#   The fixed-point equation: S = D(S) + LOOP, where D(S) stores S's chars.
#   This is solvable!  We just need |D(S)| to be consistent with |S|.
#
#   |D(S)| = sum over i=1..N of len("[i ord(S[i-1])]")
#          = sum of (2 + len(str(i)) + len(str(ord(S[i-1]))))
#            [bracket, index, space, value, bracket]
#
#   N = |D(S)| + |LOOP|
#
#   We iterate:  start with S = LOOP, compute D(S), set S = D(S)+LOOP, repeat.

def build_quine() -> str:
    """
    Compute the fixed-point Stercus quine source.

    Design: S = D(S) + LOOP, no suffix needed.
    D(S) stores every char of S in cells 1..|S|.
    LOOP reads those cells and prints them, reproducing S exactly.
    """
    # Seed
    source = LOOP
    for _ in range(500):
        data = make_data_section(source)
        new_source = data + LOOP
        if new_source == source:
            break
        source = new_source
    else:
        raise RuntimeError("Fixed point did not converge after 500 rounds")
    return source


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify(source: str) -> bool:
    """
    Simulate the quine's execution in Python and check output == source.

    Memory model: dict mapping cell index -> int value (default 0).
    Simulate: set cells from data section, then run the LOOP.
    """
    # Locate boundary between data section and LOOP
    loop_start = source.index(LOOP)
    data_section = source[:loop_start]

    # Parse and execute data section: each token is [i V]
    mem: dict[int, int] = {}
    pos = 0
    while pos < len(data_section):
        assert data_section[pos] == '[', f"expected '[' at pos {pos}"
        close = data_section.index(']', pos)
        idx_str, val_str = data_section[pos+1:close].split()
        mem[int(idx_str)] = int(val_str)
        pos = close + 1

    # Simulate LOOP: ptr starts at 1, loop while mem[ptr] != 0
    output_chars = []
    ptr = 1
    while True:
        val = mem.get(ptr, 0)
        if val == 0:
            break
        # Print '[', decimal(ptr), ' ', decimal(val), ']'
        output_chars.append('[')
        output_chars.append(str(ptr))
        output_chars.append(' ')
        output_chars.append(str(val))
        output_chars.append(']')
        ptr += 1

    output = "".join(output_chars)

    if output != source:
        # Show first difference for debugging
        for i, (a, b) in enumerate(zip(output, source)):
            if a != b:
                print(f"  First diff at char {i}: output={repr(a)} source={repr(b)}", file=sys.stderr)
                print(f"  output[{i-5}:{i+20}] = {repr(output[max(0,i-5):i+20])}", file=sys.stderr)
                print(f"  source[{i-5}:{i+20}] = {repr(source[max(0,i-5):i+20])}", file=sys.stderr)
                break
        if len(output) != len(source):
            print(f"  Length mismatch: output={len(output)} source={len(source)}", file=sys.stderr)
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Computing Stercus quine fixed point...", file=sys.stderr)
    source = build_quine()
    print(f"Source length: {len(source)} chars", file=sys.stderr)
    print(f"Printer (LOOP) length: {len(LOOP)} chars", file=sys.stderr)
    print(f"Data section length: {len(source) - len(LOOP)} chars", file=sys.stderr)

    print("Verifying (Python simulation)...", file=sys.stderr)
    ok = verify(source)
    if not ok:
        print("VERIFICATION FAILED", file=sys.stderr)
        sys.exit(1)
    print("Verification passed.", file=sys.stderr)

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "examples", "quine.cus"
    )
    with open(out_path, "w") as f:
        f.write(source)
    print(f"Written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
