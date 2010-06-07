from rpc4django import rpcmethod

@rpcmethod(signature=['int', 'int', 'int'])
def power(a, b):
    return a ** b

@rpcmethod(signature=['int', 'int'], url_ns="some_ns")
def power2(a):
    return 2 ** a
