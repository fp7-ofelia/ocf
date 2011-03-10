#TESTING RPC
from common.rpc4django import rpcmethod
@rpcmethod(signature=['string'], permission='auth.add_group')
def test2():
    return "Test Done"
