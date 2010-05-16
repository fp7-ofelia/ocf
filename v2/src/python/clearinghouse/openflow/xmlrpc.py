'''
Created on May 1, 2010

@author: jnaous
'''
from apps.rpc4django import rpcmethod
from clearinghouse.openflow.models import OpenFlowAggregate

@rpcmethod(signature=['string', 'string'])
def topology_changed(cookie, **kwargs):
    '''Reload the topology'''
    try:
        agg = OpenFlowAggregate.objects.get(pk=int(cookie))
    except OpenFlowAggregate.DoesNotExist:
        return "Invalid cookie"
    agg.update_topology()
    return ""

@rpcmethod(signature=['string', 'string'])
def ping(data):
    '''
    Test method to see that everything is up.
    return a string that is "%s: PONG" % data
    '''
    
    return "PONG: %s" % data
