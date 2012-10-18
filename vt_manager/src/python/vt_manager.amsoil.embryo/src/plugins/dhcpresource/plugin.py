import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('simpleresource')

from dhcpr.dhcpgenitwoadapter import DHCPGENI2Adapter
from dhcpr.ipresource import IPResource
from dhcpr.ipresourcemanager import IPResourceManager
        
# setup the plugin
def setup():
    # register my resourcemanager with the registry
    rm = IPResourceManager()
    rmRegistry = pm.getService('resourcemanagerregistry')
    rmRegistry.register(rm)
    
    # register my adapter with the adapterregistry
    dhcpAdapter = DHCPGENI2Adapter()
    adapterRegistry = pm.getService('adapterregistry')
    adapterRegistry.register(dhcpAdapter)

