""" Errors that may be raised during compilation of the Stercus language. """

class IndexOutOfRangeError(Exception):
    """ Raised when the program attempted to access an index outside of memory."""
    pass

class UnbalancedBracketsError(Exception):
    """ Raised when the program has an unbalanced number of brackets. """
    pass

class ApplicationNameError(Exception):
    """ Raised when a disallowed application name is encountered. """
    pass
