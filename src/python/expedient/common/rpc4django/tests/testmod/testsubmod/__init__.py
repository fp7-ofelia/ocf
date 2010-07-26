from expedient.common.rpc4django import rpcmethod

@rpcmethod(signature=['int', 'int', 'int'])
def power(a, b):
    return a ** b

@rpcmethod(signature=['int', 'int'], url_name="my_url_name")
def power2(a):
    return 2 ** a
