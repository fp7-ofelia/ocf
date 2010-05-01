
import uuid
from SecureXMLRPCServer import SecureXMLRPCServer

class ClearinghouseServer(object):
    """The public API for the Clearinghouse.  This class provides the
    XMLRPC interface and invokes a delegate for all the operations.

    """

    def __init__(self, delegate):
        self._delegate = delegate
        
    def GetVersion(self):
        return self._delegate.GetVersion()

    def Resolve(self, urn):
        return self._delegate.Resolve(urn)


class SampleClearinghouseServer(ClearinghouseServer):
    """Add Additional functionality that is not part of the geni API
    specification.

    """

    def __init__(self, delegate):
        self._delegate = delegate
        
    def CreateSlice(self):
        return self._delegate.CreateSlice()

    def ListAggregates(self):
        return self._delegate.ListAggregates()


class Clearinghouse(object):

    def __init__(self):
        pass

    def runserver(self, addr, keyfile=None, certfile=None,
                  ca_certs=None):
        """Run the clearinghouse server."""
        self.keyfile = keyfile
        self.certfile = certfile
        # Create the xmlrpc server, load the rootkeys and do the ssl thing.
        self._server = self._make_server(addr, keyfile, certfile,
                                         ca_certs)
        self._server.register_instance(SampleClearinghouseServer(self))
        print 'Listening on port %d...' % (addr[1])
        self._server.serve_forever()

    def _make_server(self, addr, keyfile=None, certfile=None,
                     ca_certs=None):
        """Creates the XML RPC server."""
        return SecureXMLRPCServer(addr, keyfile=keyfile, certfile=certfile,
                                  ca_certs=ca_certs)

    def GetVersion(self):
        version = dict()
        version['geni_api'] = 1
        version['pg_api'] = 2
        version['geni_stitching'] = False
        return version

    def Resolve(self, urn):
        result = dict()
        dict['urn'] = urn
        return result

    def CreateSlice(self):
        import sfa.trust.gid as gid
        # Create a random uuid for the slice
        slice_uuid = uuid.uuid4()
        # Where was the slice created?
        (ipaddr, port) = self._server.socket._sock.getsockname()
        public_id = 'IDN geni.net//slice//%s//%s:%d' % (slice_uuid,
                                                        ipaddr,
                                                        port)
        urn = urn_to_publicid(public_id)
        # Create a credential authorizing this user to use this slice.
        slice_gid = self.create_slice_gid(slice_uuid, urn)[0]
        # Get the creator info from the peer certificate
        user_gid = gid.GID(string=str(self._server.pem_cert))
        try:
            slice_cred = self.create_slice_credential(user_gid,
                                                      slice_gid)
        except Exception:
            import traceback
            traceback.print_exc()
            raise
        print 'Created slice %r' % (urn)
        return slice_cred.save_to_string()

    def ListAggregates(self):
        return list()
    
    def create_slice_gid(self, subject, slice_urn):
        import sfa.trust.gid as gid
        import sfa.trust.certificate as cert
        newgid = gid.GID(create=True, uuid=gid.create_uuid(), urn=slice_urn)
        keys = cert.Keypair(create=True)
        newgid.set_pubkey(keys)
        issuer_key = cert.Keypair(filename=self.keyfile)
        issuer_cert = cert.Certificate(filename=self.certfile)
        newgid.set_issuer(issuer_key, cert=issuer_cert)
        newgid.encode()
        newgid.sign()
        return newgid, keys

    def create_slice_credential(self, user_gid, slice_gid):
        import sfa.trust.credential as cred
        import sfa.trust.rights as rights
        ucred = cred.Credential()
        ucred.set_gid_caller(user_gid)
        ucred.set_gid_object(slice_gid)
        ucred.set_lifetime(3600)
        privileges = rights.determine_rights('user', None)
        privileges.add('embed')
        ucred.set_privileges(privileges)
        ucred.encode()
        ucred.set_issuer_keys(self.keyfile, self.certfile)
        ucred.sign()
        return ucred

# We could probably define a list of transformations (replacements)
# and run it forwards to go to a publicid. Then we could run it
# backwards to go from a publicid.

# Perform proper escaping. The order of these rules matters
# because we want to catch things like double colons before we
# translate single colons. This is only a subset of the rules.
publicid_xforms = [(' ', '+'),
                   ('::', ';'),
                   (':', '%3A'),
                   ('//', ':')]


def urn_from_publicid(id):
    for a, b in reversed(publicid_xforms):
        id = id.replace(b, a)
    return id

def urn_to_publicid(id):
    for a, b in publicid_xforms:
        id = id.replace(a, b)
    # prefix with 'urn:publicid:'
    return 'urn:publicid:' + id
