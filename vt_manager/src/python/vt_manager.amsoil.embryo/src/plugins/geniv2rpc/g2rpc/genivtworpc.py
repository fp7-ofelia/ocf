import random
import os, os.path
from lxml import etree

import ext.geni
import ext.sfa.trust.gid as gid

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('geniv2api')

from genitwoadapterbase import GENI2AdapterBase
from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GENIv2RPC(xmlrpc.Dispatcher):
    """This class implements all GENI methods and delegates these to the adapters registered with the adapter registry, but only to the adapters which implement GENI2AdapterBase.

    Please find the API documentation via the GENI wiki: http://groups.geni.net/geni/wiki/GAPI_AM_API_V2

    Authentication pseudocode:
        st = pm.getService('contextstorage')
        user_id = getOrCreateUserIdFromThisPluginsDatabase(user_urn) # returns GUID which has been saved to this thread's database
        st['user'] = getContextObjFromAuthorziation(user_id) # this will get persisted
        st['user_info'] = { ... } # this not persisted
        st['request_data'] = { post_data, certs, ... }
    """
    
    RSPEC3_NAMESPACE= 'http://www.geni.net/resources/rspec/3'
    
    def __init__(self):
        super(GENIv2RPC, self).__init__(logger)

    def GetVersion(self):
        """Returns the version of this interface.
        This method can be hard coded, since we are actually setting up the GENI v2 API, only."""
        # no authentication necessary
        
        adapterRegistry = pm.getService('adapterregistry')
        supportedAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)
        
        request_extensions = [(a.rspec3_request_extensions) for a in supportedAdapters]
        ad_extensions = [(a.rspec3_advertisement_extensions) for a in supportedAdapters]
        
        request_rspec_versions = [
            { 'type' : 'geni', 'version' : '3', 'schema' : 'http://www.geni.net/resources/rspec/3/request.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/3', 'extensions' : request_extensions},]
        ad_rspec_versions = [
                { 'type' : 'geni', 'version' : '3', 'schema' : 'http://www.geni.net/resources/rspec/3/ad.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/3', 'extensions' : ad_extensions },]

        return {
            'geni_api' : 2,
            'code'       : { 'geni_code' : 0 },
            'value'      : { 'geni_api' : 2,
                'geni_request_rspec_versions'   : request_rspec_versions,
                'geni_ad_rspec_versions'        : ad_rspec_versions,
                },
            'output'     : ''
        }

    def ListResources(self, credentials, options):
        """
        ListResources pseudocode:
            ...auth...
            results = []
            for adapter in supportedAdapters:
                results += adapter.list()
            merge(results)
            return results
        """
        # Authentication
        context=self._setupContext(credentials, None)
        
        adapterRegistry = pm.getService('adapterregistry')
        supportedAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)
        results = []
        
        # assemble parameters
        params = {}
        if 'geni_slice_urn' in options and options['geni_slice_urn']:
            params['slice_urn'] = options['slice_urn']
        if 'geni_available' in options and options['geni_available']:
            params['available'] = options['geni_available']

        # get listing from all supported adapters
        for adapter in supportedAdapters:
            results.append(adapter.geni2ListResources(**params))

        # create RSpec advertisement
        rspec = self._lxml_rspec_root('advertisement', supportedAdapters)
        for res in results:
            self._appendReturnValue(rspec, res)
        result = etree.tostring(rspec, pretty_print=True)

        # return the result
        if 'geni_compressed' in options and options['geni_compressed']:
            result = base64.b64encode(zlib.compress(result))
        return { 'code' : { 'geni_code' : 0 }, 'value' : result, 'output' : '' }
        
    def CreateSliver(self, sliceURN, credentials, rspec, users, options):
        """
        CreateSlivers pseudocode:
            parsedRSpec = parse(parameter)
            for rspecPart in parsedRSpec: # discriminated by slivertype and or schema
                # remove unsupported adapters
                for adapter in supportedAdapters:
                    if not adapter.supportsSliverType(rspecPart[sliverType])
                        removefromSupportedAdapters
                # choose from the remaining supportedAdapters if parsedRSpec[component_id] was given # adapters have to create component_id
                # otherwise take a random one (this can fail due because the actual adapter can not fulfill the request, so try the next adapter left in the list)
                supportedAdapter[0].createSliver(rspecPart)
        """
        context=self._setupContext(credentials, None)
        # get services and supported adapters
        adapterRegistry = pm.getService('adapterregistry')
        geniAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)
        # split rspec into parts
        dom = etree.fromstring(rspec)
        if (dom.tag != ("{%s}rspec" % (self.RSPEC3_NAMESPACE,))):
            raise MalformedRSpec3Error("Root node is not <rspec> or is not in namespace" % (self.RSPEC3_NAMESPACE,))

        results = []
        for partElm in dom:
            # assemble the list of adapters which support the given sliver_type
            sTypeAdapters = []
            for adapter in geniAdapters:
                if (adapter.supportsSliverType(partElm)):
                    sTypeAdapters.append(adapter)
            # pick one and delegate the call
            chosenAdapter = self._chooseAdapter(sTypeAdapters, partElm)
            results.append(chosenAdapter.geni2CreateSliver(sliceURN, partElm, rspec, users, **options))
        
        # assemble the RSpec and return it
        rspec = self._lxml_rspec_root('manifest', [chosenAdapter])
        for result in results:
            self._appendReturnValue(rspec, result)
        rspecStr = etree.tostring(rspec, pretty_print=True)
        return { 'code' : { 'geni_code' : 0 }, 'value' : rspecStr, 'output' : '' }


    def DeleteSliver(self, sliceURN, credentials, options):
        context=self._setupContext(credentials, sliceURN)
        
        adapterRegistry = pm.getService('adapterregistry')
        geniAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)
        
        result = True
        for adapter in geniAdapters:
            result = result and adapter.geni2DeleteSliver(sliceURN, **options)
        
        return { 'code' : { 'geni_code' : 0 }, 'value' : True, 'output' : '' }

    def SliverStatus(self, sliceURN, credentials, options):
        context=self._setupContext(credentials, sliceURN)
        
        adapterRegistry = pm.getService('adapterregistry')
        supportedAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)
        results = []
        
        # get listing from all supported adapters
        for adapter in supportedAdapters:
            results += adapter.geni2SliverStatus(sliceURN, **options)

        return { 'code' : { 'geni_code' : 0 }, 'value' : results, 'output' : '' }

        
    def RenewSliver(self, sliceURN, credentials, exparationTime, options):
        context=self._setupContext(credentials, sliceURN)
        
        adapterRegistry = pm.getService('adapterregistry')
        supportedAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)

        result = True
        for adapter in supportedAdapters:
            result = result and adapter.geni2RenewSliver(sliceURN, exparationTime, **options)
        return { 'code' : { 'geni_code' : 0 }, 'value' : result, 'output' : '' }
        
    def Shutdown(self, sliceURN, credentials, options):
        context=self._setupContext(credentials, sliceURN)
        
        adapterRegistry = pm.getService('adapterregistry')
        supportedAdapters = adapterRegistry.getAdapters(GENI2AdapterBase)

        result = True
        for adapter in supportedAdapters:
            result = result and adapter.geni2Shutdown(sliceURN, **options)
        return { 'code' : { 'geni_code' : 0 }, 'value' : result, 'output' : '' }
        

    def _setupContext(self, credentials, sliceURN=None):
        """Creates a request context and returns the context to the caller."""
        # check the certificate
        certificate = self.requestCertificate()
        if certificate != None:
            config = pm.getService("config")
            cert_root = config.Config.getConfigItem("geniv2rpc.cert_root").getValue()

            cred_verifier = ext.geni.CredentialVerifier(os.path.expanduser(cert_root))
            cred_verifier.verify_from_strings(certificate, credentials, sliceURN, []) # cred_verifier.verify_from_strings(user_cert, credentials, sliceURN, required_privileges_list)
            uinfo = gid.GID(string=certificate)
            user_id = uinfo.get_urn()
            # TODO we might need to add privileges from the cert to the context too
        else: # there was no certificate, so we assume we are in development mode
            user_id = 'unknown_user'

        # actually create the context and set the additional data
        contextKlass = pm.getService('context')
        context = contextKlass(user_id, 'geni', 2)
        context.data['certificate'] = certificate
        context.data['credentials'] = credentials
        return context



    def _chooseAdapter(self, adapters, lxmlElm):
        if (len(adapters) == 0):
            raise SliverTypeNotSupportedError(lxmlElm.tag)
        if (len(adapters) > 1):
            self._log.info("Choosing randomly from adapters (%s) to fulfill the RSpec part <'%s'>" % (', '.join([a.__class__.__name__ for a in adapters]), lxmlElm.tag))
            return adapters[random.randint(0, len(adapters)-1)]
        else:
            return adapters[0]

    def _appendReturnValue(self, rootNode, value):
        if type(value) is list:
            for node in value:
                rootNode.append(node)
        else: # assume to be an lxml Element
            rootNode.append(value)

    def _lxml_rspec_root(self, rspec_type, adapters):
        """
        Returns the xml root node with the namespace extensions in the given {adapters}.
        {adapters} must be a list of GENI2AdapterBase objects
        {rspec_type} should be either 'advertisement' or 'manifest'
        """
        if rspec_type == 'advertisement':
            ad_extensions = {} # assemble merged dictionary
            for a in adapters:
                ad_extensions.update(a.rspec3_advertisement_extensions)
            return etree.Element('rspec', ad_extensions, type='advertisement')
        # elif rspec_type == 'request': "http://www.geni.net/resources/rspec/3/request.xsd " + " ".join(...)
        elif rspec_type == 'manifest':
            manifest_extensions = {} # assemble merged dictionary
            for a in adapters:
                manifest_extensions.update(a.rspec3_manifest_extensions)
            return etree.Element('rspec', manifest_extensions, type='manifest')
        else:
            raise ValueError('RSpec type not supported by this method.')

