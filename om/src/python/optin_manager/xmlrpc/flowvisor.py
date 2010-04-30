'''
Created on Apr 29, 2010

@author: jnaous
'''
from rpc4django import rpcmethod

@rpcmethod(signature=[])
def topology_changed(**kwargs):
    '''
    This is a callback from the flowvisor when the topology changes.
    '''
    pass
