""" Stercus Language Constants """

C_DATA_ARRAY_NAME = "_STERCUS_DATA"
C_FUNC_ARG_NAME = "s0"
STERCUS_ARG_NAME = "$"


# Brackets.
APPLICATOR = {
    "OPEN": "[",
    "CLOSE": "]",
}

APPLICATION = {
    "OPEN": "{",
    "CLOSE": "}",
}

CONDITIONAL = {
    "OPEN": "(",
    "CLOSE": ")",
}

BRACKETS = {
    "PAIRS": {
        APPLICATOR["OPEN"]: APPLICATOR["CLOSE"],
        APPLICATION["OPEN"]: APPLICATION["CLOSE"],
        CONDITIONAL["OPEN"]: CONDITIONAL["CLOSE"],
    }
}
BRACKETS["OPEN"] = list(BRACKETS["PAIRS"].keys())
BRACKETS["CLOSE"] = list(BRACKETS["PAIRS"].values())
BRACKETS["ALL"] = BRACKETS["OPEN"] + BRACKETS["CLOSE"]

# Comments.
SINGLE_LINE_COMMENT_DELIMITER = "#"
MULTI_LINE_COMMENT_DELIMITER = "##"

# Built-in applications.
INCREMENT = "+"
DECREMENT = "-"
OUTPUT_INT = "."
OUTPUT_CHAR = ":"
INPUT = ","
NOP = "_"
