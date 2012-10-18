from lxml.builder import ElementMaker

import amsoil.core.pluginmanager as pm
from ipresource import IPResource
from util.ip import IP

GENI2AdapterBase = pm.getService('geni2adapterbase')

class DHCPGENI2Adapter(GENI2AdapterBase):
    rspec3_advertisement_extensions = {'dhcp': 'http://example.com/dhcp/ad.xsd'}
    rspec3_request_extensions = {'dhcp': 'http://example.com/dhcp/req.xsd'}
    rspec3_manifest_extensions = {'dhcp': 'http://example.com/dhcp/mani.xsd'}

    def supportsSliverType(self, lxmlNode):
        return (lxmlNode.tag == self._pnsR('ip')) or (lxmlNode.tag == self._pnsR("iprange"))
    
    def geni2ListResources(self, **options):
        # context = pm.getService('context').currentContext() # This is how you access user data
        # logger.info(context.user_id)
        # logger.info(context.data['certificate'])

        rmRegistry = pm.getService('resourcemanagerregistry')
        managers = rmRegistry.getManagers(IPResource)

        resources = [] # get all resources from the manager
        # Omited interpreting options for simplicity
        for rm in managers:
            resources += rm.list()
        
        result = [] # translate all resources to a format which the GENI RPC understands (in this case a list of lxml elements)
        E = self._getDHCPAdElementMaker()
        for r in resources:
            rRep = E.resource(uuid=str(r.uuid))
            rRep.append(E.ip(str(r.ip)))
            result.append(rRep)
        return result

    def geni2CreateSliver(self, sliceURN, lxmlRSpecPart, fullRequestRspec, users, **options):
        rmRegistry = pm.getService('resourcemanagerregistry')
        manager = rmRegistry.getRandomManager(IPResource)

        if lxmlRSpecPart.tag == self._pnsR('ip'): # deal with ip tags
            ip = IP.fromstring(lxmlRSpecPart.text.strip())
            resource = manager.reserve(None, ip=ip)
            
            E = self._getDHCPManifestElementMaker()
            rRep = E.resource(uuid=str(resource.uuid))
            rRep.append(E.ip(str(resource.ip)))
            return rRep
        elif lxmlRSpecPart.tag == self._pnsR('iprange'): # deal with ip ranges
            fromIP = IP.fromstring(lxmlRSpecPart.find(self._pnsR('from')).text.strip())
            toIP = IP.fromstring(lxmlRSpecPart.find(self._pnsR('to')).text.strip())
            # reserve all IPs in range
            resources = []
            for ip in fromIP.upto(toIP):
                resources.append(manager.reserve(None, ip=ip)) # this might throw errors
            
            # assemble resulting tree
            E = self._getDHCPManifestElementMaker()
            resultRep = E.range()
            for resource in resources:
                rRep = E.resource(uuid=str(resource.uuid))
                rRep.append(E.ip(str(resource.ip)))
                resultRep.append(rRep)
            return resultRep
        else:
            raise RuntimeError('This request should not have been dispatched here, because the type is not supported (please see supportsSliverType).')

    def geni2DeleteSliver(self, sliceURN, **options):
        rmRegistry = pm.getService('resourcemanagerregistry')
        managers = rmRegistry.getManagers(IPResource)
        
        for rm in managers:
            resources = rm.findBySliceURN(sliceURN)
            for resource in resources:
                rm.release(resource.uuid)
        return True # no exception, so it must be successful
        

    def geni2SliverStatus(self, sliceURN, **options):
        rmRegistry = pm.getService('resourcemanagerregistry')
        managers = rmRegistry.getManagers(IPResource)
        
        result = []
        for rm in managers:
            resources = rm.findBySliceURN(sliceURN)
            for resource in resources:
                result.append({ 'geni_urn' : str(resource.uuid), 'geni_status' : resource.getOperationalState(), 'geni_error' : ''})
        return result
        
    def geni2RenewSliver(self, sliceURN, exparationTime, **options):
        rmRegistry = pm.getService('resourcemanagerregistry')
        managers = rmRegistry.getManagers(IPResource)
        
        for rm in managers:
            resources = rm.findBySliceURN(sliceURN)
            for resource in resources:
                try:
                    resource.renew(exparationTime)
                except:
                    return False
        return True

    def geni2Shutdown(self, sliceURN, **options):
        rmRegistry = pm.getService('resourcemanagerregistry')
        managers = rmRegistry.getManagers(IPResource)
        
        for rm in managers:
            resources = rm.findBySliceURN(sliceURN)
            for resource in resources:
                try:
                    resource.stop()
                except:
                    return False
        return True
    
    def _getDHCPAdElementMaker(self):
        return ElementMaker(namespace=self.rspec3_advertisement_extensions['dhcp'], nsmap=self.rspec3_advertisement_extensions)
    
    def _getDHCPManifestElementMaker(self):
        return ElementMaker(namespace=self.rspec3_manifest_extensions['dhcp'], nsmap=self.rspec3_manifest_extensions)

    def _pnsA(self, tagname):
        """convenience method: prepend advertisement namespace to a tagname"""
        return "{%s}%s" % (self.rspec3_advertisement_extensions['dhcp'], tagname)
    def _pnsM(self, tagname):
        """convenience method: prepend manifest namespace to a tagname"""
        return "{%s}%s" % (self.rspec3_manifest_extensions['dhcp'], tagname)
    def _pnsR(self, tagname):
        """convenience method: prepend request namespace to a tagname"""
        return "{%s}%s" % (self.rspec3_request_extensions['dhcp'], tagname)
