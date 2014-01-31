#
# Shared type definitions
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#

from types import NoneType, IntType, LongType, FloatType, StringTypes, DictType, TupleType, ListType
from foam.sfa.util.faults import SfaAPIError

class Parameter:
    """
    Typed value wrapper. Use in accepts and returns to document method
    parameters. Set the optional and default attributes for
    sub-parameters (i.e., dict fields).
    """

    def __init__(self, type, doc = "",
                 min = None, max = None,
                 optional = None,
                 ro = False,
                 nullok = False):
        # Basic type of the parameter. Must be a builtin type
        # that can be marshalled by XML-RPC.
        self.type = type

        # Documentation string for the parameter
        self.doc = doc

        # Basic value checking. For numeric types, the minimum and
        # maximum possible values, inclusive. For string types, the
        # minimum and maximum possible UTF-8 encoded byte lengths.
        self.min = min
        self.max = max

        # Whether the sub-parameter is optional or not. If None,
        # unknown whether it is optional.
        self.optional = optional

        # Whether the DB field is read-only.
        self.ro = ro

        # Whether the DB field can be NULL.
        self.nullok = nullok

    def type(self):
        return self.type

    def __repr__(self):
        return repr(self.type)

class Mixed(tuple):
    """
    A list (technically, a tuple) of types. Use in accepts and returns
    to document method parameters that may return mixed types.
    """

    def __new__(cls, *types):
        return tuple.__new__(cls, types)


def python_type(arg):
    """
    Returns the Python type of the specified argument, which may be a
    Python type, a typed value, or a Parameter.
    """

    if isinstance(arg, Parameter):
        arg = arg.type

    if isinstance(arg, type):
        return arg
    else:
        return type(arg)

def xmlrpc_type(arg):
    """
    Returns the XML-RPC type of the specified argument, which may be a
    Python type, a typed value, or a Parameter.
    """

    arg_type = python_type(arg)

    if arg_type == NoneType:
        return "nil"
    elif arg_type == IntType or arg_type == LongType:
        return "int"
    elif arg_type == bool:
        return "boolean"
    elif arg_type == FloatType:
        return "double"
    elif arg_type in StringTypes:
        return "string"
    elif arg_type == ListType or arg_type == TupleType:
        return "array"
    elif arg_type == DictType:
        return "struct"
    elif arg_type == Mixed:
        # Not really an XML-RPC type but return "mixed" for
        # documentation purposes.
        return "mixed"
    else:
        raise SfaAPIError, "XML-RPC cannot marshal %s objects" % arg_type
