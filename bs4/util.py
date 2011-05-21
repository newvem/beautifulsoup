# Helper functions and mixin classes for Beautiful Soup

import types
try:
    set
except NameError:
    from sets import Set as set

def buildSet(args=None):
    """Turns a list or a string into a set."""
    if isinstance(args, str):
        return set([args])
    if args is None:
        return set()
    return set(args)
