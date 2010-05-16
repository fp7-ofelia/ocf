from apps.rpc4django import rpcmethod
from optin_manager.xmlrpc_server.models import CallBackServerProxy


@rpcmethod(signature=[])
def topology_changed(**kwargs):
    '''
    This is a callback from the flowvisor when the topology changes.
    It also updates the OM Topology db
    '''
    for sp in CallBackServerProxy.objects.all():
        sp.topology_changed(sp.cookie)
