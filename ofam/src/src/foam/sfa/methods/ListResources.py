import zlib

from foam.sfa.util.xrn import urn_to_hrn
from foam.sfa.util.faults import SfaInvalidArgument
from foam.sfa.trust.credential import Credential
from foam.sfa.trust.auth import Auth

class ListResources:

    def __init__(self, creds, options, **kwargs):
       
        # client must specify a version
        if not options.get('geni_rspec_version'):
            if options.get('rspec_version'):
                options['geni_rspec_version'] = options['rspec_version']
            else:
                raise SfaInvalidArgument('Must specify an rspec version option. geni_rspec_version cannot be null')
 
        # get slice's hrn from options    
        xrn = options.get('geni_slice_urn', '')
        (hrn, _) = urn_to_hrn(xrn)

        # Find the valid credentials
        #valid_creds = self.api.auth.checkCredentials(creds, 'listnodes', hrn)
        valid_creds = Auth().checkCredentials(creds, 'listnodes', hrn)
        # get hrn of the original caller 
        origin_hrn = options.get('origin_hrn', None)
        if not origin_hrn:
            origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()
        origin_gid = Credential(string=valid_creds[0]).get_gid_caller()

        #rspec = AggregateManager(None).ListResources(self.api, creds, options)

        #chain_name = 'OUTGOING'
        #if options.has_key('geni_compressed') and options['geni_compressed'] == True:
        #    rspec = zlib.compress(rspec).encode('base64')

        #return rspec  
        #return True
        return
    
    
