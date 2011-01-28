# Helper functions and mixin classes for Beautiful Soup

import types
try:
    set
except NameError:
    from sets import Set as set

def isList(l):
    """Convenience method that works with all 2.x versions of Python
    to determine whether or not something is listlike."""
    return ((hasattr(l, '__iter__') and not isString(l))
            or (type(l) in (types.ListType, types.TupleType)))

def isString(s):
    """Convenience method that works with all 2.x versions of Python
    to determine whether or not something is stringlike."""
    try:
        return isinstance(s, unicode) or isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)

def buildSet(args=None):
    """Turns a list or a string into a set."""
    if isinstance(args, str):
        return set([args])
    if args is None:
        return set()
    return set(args)
