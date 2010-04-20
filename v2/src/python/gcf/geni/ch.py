
import datetime
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

    def runserver(self, addr, basedir='.', keyfile=None, certfile=None,
                  ca_certs=None):
        """Run the clearinghouse server."""
        # Create the xmlrpc server, load the rootkeys and do the ssl thing.
        self._server = self._make_server(addr, basedir, keyfile, certfile,
                                         ca_certs)
        self._server.register_instance(SampleClearinghouseServer(self))
        self._server.serve_forever()

    def _make_server(self, addr, basedir='.', keyfile=None, certfile=None,
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
        # Create a random uuid for the slice
        slice_uuid = uuid.uuid4()
        # Who created the slice? For now the tuple representation of
        # the subject in the cert.
        owner = self._server.peercert['subject']
        # When does the slice expire? For now, 60 minutes in the future.
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=60)
        # Where was the slice created?
        (ipaddr, port) = self._server.socket._sock.getsockname()
        public_id = 'IDN geni.net//slice//%s//%s:%d' % (slice_uuid,
                                                        ipaddr,
                                                        port)
        urn = urn_to_publicid(public_id)
        template = '<credential type="slice" urn="%s" expiration=%s/>'
        return template % (urn, expiration)

    def ListAggregates(self):
        return list()


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
