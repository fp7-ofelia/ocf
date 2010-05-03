'''
Created on Apr 29, 2010

@author: jnaous
'''
from rpc4django import rpcmethod
from optin_manager.xmlrpc_server.models import CallBackServerProxy

@rpcmethod(signature=[])
def topology_changed(**kwargs):
    '''
    This is a callback from the flowvisor when the topology changes.
    '''
    for sp in CallBackServerProxy.objects.all():
        sp.topology_changed(sp.cookie)
