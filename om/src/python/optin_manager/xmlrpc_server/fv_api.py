from apps.rpc4django import rpcmethod
from optin_manager.xmlrpc_server.models import CallBackServerProxy, CallBackFVProxy
from optin_manager.flowspace.models import Topology

@rpcmethod(signature=[])
def topology_changed(**kwargs):
    '''
    This is a callback from the flowvisor when the topology changes.
    It also updates the OM Topology db
    '''
    CallBackFVProxy.updateTopology()
    for sp in CallBackServerProxy.objects.all():
        sp.topology_changed(sp.cookie)
