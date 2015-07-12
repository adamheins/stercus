""" Stercus Language Constants """

# Size of data available to the program (in bytes).
DATA_SIZE = 10000

# Brackets.
APPLICATOR = {
    'OPEN': '[',
    'CLOSE': ']',
}

APPLICATION = {
    'OPEN': '{',
    'CLOSE': '}',
}

CONDITIONAL = {
    'OPEN': '(',
    'CLOSE': ')',
}

BRACKETS = {
    'PAIRS': {
        APPLICATOR['OPEN']: APPLICATOR['CLOSE'],
        APPLICATION['OPEN']: APPLICATION['CLOSE'],
        CONDITIONAL['OPEN']: CONDITIONAL['CLOSE'],
    }
}
BRACKETS['OPEN'] = BRACKETS['PAIRS'].keys()
BRACKETS['CLOSE'] = BRACKETS['PAIRS'].values()
BRACKETS['ALL'] = BRACKETS['OPEN'] + BRACKETS['CLOSE']

# Comments.
SINGLE_LINE_COMMENT_DELIMITER = '#'
MULTI_LINE_COMMENT_DELIMITER = '##'

# Built-in applications.
INCREMENT = '+'
DECREMENT = '-'
OUTPUT = '.'
INPUT = ','
NOP = '_'
