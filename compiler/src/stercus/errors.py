""" Errors that may be raised during compilation of the Stercus language. """

class AddressOutOfRangeError(Exception):
    """ Raised when the program attempted to access an address outside the range
        of STERCUS_DATA_SIZE. """
    pass

class UnbalancedBracketsError(Exception):
    """ Raised when the program has an unbalanced number of brackets. """
    pass

class FunctionNameError(Exception):
    """ Raised when a disallowed function name is encountered. """
    pass
