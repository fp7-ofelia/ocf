'''
Created on May 1, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
from models import OpenFlowAggregate

# TODO: change this to be protected by some authentication
@rpcmethod(signature=['string', 'string'], url_name="openflow_open_xmlrpc")
def topology_changed(cookie, **kwargs):
    '''Reload the topology'''
    try:
        agg = OpenFlowAggregate.objects.get(pk=int(cookie))
    except OpenFlowAggregate.DoesNotExist:
        return "Invalid cookie"
    agg.update_topology()
    return ""

@rpcmethod(signature=['string', 'string'], url_name="openflow_open_xmlrpc")
def ping(data):
    '''
    Test method to see that everything is up.
    return a string that is "%s: PONG" % data
    '''
    
    return "PONG: %s" % data

