#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------
"""
Reference GENI GCF Clearinghouse. Uses SFA Certificate and credential objects.
NOTE it requires a user cert at startup to get the full certificate chain.
Run from gch.py
Will produce signed user credentials from a GID, return a
(hard coded) list of aggregates, and create a new Slice Credential.

"""

import logging
import os
import uuid

from SecureXMLRPCServer import SecureXMLRPCServer
from verifier import CredentialVerifier
import gcf.sfa.trust.gid as gid
import gcf.sfa.trust.certificate as cert
import gcf.sfa.trust.credential as cred
import gcf.sfa.trust.rights as rights

# Substitute eg "openflow//stanford ch"
#SLICEPUBID_PREFIX = "geni.net//gpo//gcf"
SLICEPUBID_PREFIX = "openflow//stanford ch"
SLICE_GID_SUBJ = "gcf.slice"

USER_CRED_LIFE = 86400
SLICE_CRED_LIFE = 3600

# The list of Aggregates that this Clearinghouse knows about
# should be defined in the geni_aggregates file
# ListResources will refer the client to these aggregates
# Clearinghouse.runserver currently does the register_aggregate_pair
# calls for each row in that file
# but this should be doable dynamically
# STANFORDMYPLC = ('urn:publicid:IDN+plc:stanford+authority+openflow',
#             'http://myplc.openflow.stanford.edu:12348')
# TESTGCFAM = ('urn:publicid:IDN+geni.net:gpo+authority+gcf', 
#              'http://127.0.0.1:8001') 
# STANFORDOIM = ('FIXMEJAD', 'FIXMEJAD')

#OTHERGPOMYPLC = ('urn:publicid:IDN+plc:gpo+authority+site2',
                   #'http://128.89.81.74:12348')
#ELABINELABAM = ('urn:publicid:IDN+elabinelab.geni.emulab.net',
                #'https://myboss.elabinelab.geni.emulab.net:443/protogeni/xmlrpc/am')

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
        
    def CreateSlice(self, urn=None):
        return self._delegate.CreateSlice(urn_req=urn)

    def DeleteSlice(self, urn):
        return self._delegate.DeleteSlice(urn)

    def ListAggregates(self):
        return self._delegate.ListAggregates()
    
    # FIXMEJAD: Do you want this method exposed?
    def CreateUserCredential(self, cert):
        return self._delegate.CreateUserCredential(cert)


class Clearinghouse(object):

    def __init__(self):
        self.logger = logging.getLogger('gch')
        self.slices = {}
        self.aggs = []

    def register_aggregate_pair(self, aggpair):
        '''Add an aggregate URN and URL pair to the known set. URL is unverified'''
        if aggpair is None:
            self.logger.debug('Null aggpair ignored')
            return
        if len(aggpair) != 2:
            self.logger.debug('Len %d aggpair ignored', len(aggpair))
            return
        if aggpair[0] is None or aggpair[0].strip() == "":
            self.logger.debug('Empty URN in Aggpair - ignore')
            return
        if aggpair[1] is None or aggpair[1].strip() == "":
            self.logger.debug('Empty URL in Aggpair for URN %s: ignore', aggpair[0])
            return

        # TODO: Avoid dupes, confirm the AM is reachable, ?
        # Real CH would require an AM contact, AM cert, ?
        self.logger.info("Registering AM %r", aggpair)
        self.aggs.append(aggpair)
        
        # ca_certs is a file of 1 ca cert possibly, preferably a dir of several
    def runserver(self, addr, keyfile=None, certfile=None,
                  ca_certs=None, user_cert=None, aggfile=None):
        """Run the clearinghouse server."""
        self.keyfile = keyfile
        self.certfile = certfile
        self.usercert = user_cert
        

        # Error check the keyfile, certfile, usercert all exist
        if keyfile is None or not os.path.isfile(os.path.expanduser(keyfile)):
            raise Exception("Missing CH key file %s" % keyfile)
        if certfile is None or not os.path.isfile(os.path.expanduser(certfile)):
            raise Exception("Missing CH cert file %s" % certfile)
        if user_cert is None or not os.path.isfile(os.path.expanduser(user_cert)):
            raise Exception("Missing user cert file %s" % user_cert)

        if ca_certs is None:
            raise Exception("Missing CA cert(s) arg")

        if not os.path.exists(os.path.expanduser(ca_certs)):
            raise Exception("Missing CA cert(s): %s" % ca_certs)

        # Load up the aggregates
#        print aggfile
        if os.path.isfile(aggfile):
            for line in file(aggfile):
                spl = line.strip().split(',')
                if len(spl) == 2:
                    self.register_aggregate_pair((spl[0].strip(),spl[1].strip()))
        self.logger.info("%d Aggregate Managers registered from aggregates file %r", len(self.aggs), aggfile)

        # This is the arg to _make_server
        ca_certs_onefname = CredentialVerifier.getCAsFileFromDir(ca_certs)

        # This is used below by CreateSlice
        self.ca_cert_fnames = []
        if os.path.isfile(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.expanduser(ca_certs)]
        elif os.path.isdir(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.join(os.path.expanduser(ca_certs), name) for name in os.listdir(os.path.expanduser(ca_certs)) if name != CredentialVerifier.CATEDCERTSFNAME]

        # Create the xmlrpc server, load the rootkeys and do the ssl thing.
        self._server = self._make_server(addr, keyfile, certfile,
                                         ca_certs_onefname)
        self._server.register_instance(SampleClearinghouseServer(self))
        self.logger.info('GENI CH Listening on port %d...' % (addr[1]))
        self._server.serve_forever()

    def _make_server(self, addr, keyfile=None, certfile=None,
                     ca_certs=None):
        """Creates the XML RPC server."""
        # ca_certs is a file of concatenated certs
        return SecureXMLRPCServer(addr, keyfile=keyfile, certfile=certfile,
                                  ca_certs=ca_certs)

    def GetVersion(self):
        self.logger.info("Called GetVersion")
        version = dict()
        version['geni_api'] = 1
        version['pg_api'] = 2
        version['geni_stitching'] = False
        return version

    def Resolve(self, urn):
        self.logger.info("Called Resolve URN %s" % urn)
        result = dict()
        result['urn'] = urn
        return result

    def CreateSlice(self, urn_req = None):
        self.logger.info("Called CreateSlice URN REQ %r" % urn_req)
        if urn_req and self.slices.has_key(urn_req):
            return self.slices[urn_req].save_to_string()
        
        # Create a random uuid for the slice
        slice_uuid = uuid.uuid4()
        # Where was the slice created?
        (ipaddr, port) = self._server.socket._sock.getsockname()
        # FIXME: Get public_id start from a properties file
        public_id = 'IDN %s slice %s//%s:%d' % (SLICEPUBID_PREFIX, slice_uuid.__str__()[4:12],
                                                                   ipaddr,
                                                                   port)
        if urn_req:
            urn = urn_req
        else:
            urn = publicid_to_urn(public_id)

        # Create a credential authorizing this user to use this slice.
        slice_gid = self.create_slice_gid(slice_uuid, urn)[0]

        # Get the creator info from the peer certificate

#        # We only know of one user cert, passed in at command line
#        user_gid = gid.GID(filename=self.usercert)

#        user_gid = gid.GID(string=str(self._server.pem_cert))

        # The problem with self._server.pem_cert is it doesn't
        # include the chain! But we accepted it, so it is signed
        # by one of our trusted certs. If the trusted certs includes
        # the CH that issued that user cert, then we are still OK.

        # So this block of code tries all the trusted certs to see if any of these
        # signed this user's cert. If so, we append that cert
        # to the user cert, in hopes of having enough info

        user_cert = cert.Certificate(string=self._server.pem_cert)
        serverstr = ""
        for cafname in self.ca_cert_fnames:
            try:
                cacert = cert.Certificate(filename=cafname)
                if user_cert.is_signed_by_cert(cacert):
                    serverstr = cacert.save_to_string(True)
                    break
                else:
#                    print 'user cert not signed by that server'
                    pass
            except Exception, exc:
                pass
            
        if serverstr == "":
            self.logger.error('Failed to generate complete user cert using trusted CAs. For user %s didnt find issuer %s cert', user_cert.get_subject(), user_cert.get_issuer())            

            # use the commandline user cert for test purposes? Raise an exception?
            # HACK!
            user_gid = gid.GID(filename=self.usercert)
        else:
            user_gid = gid.GID(string=str(self._server.pem_cert + serverstr))

        try:
            slice_cred = self.create_slice_credential(user_gid,
                                                      slice_gid)
        except Exception:
            import traceback
            self.logger.error('CreateSlice failed to get slice credential for user %r, slice %r: %s', user_gid, slice_gid, traceback.print_exc())
            raise
        self.logger.info('Created slice %r' % (urn))
        
        self.slices[urn] = slice_cred
        
        return slice_cred.save_to_string()

    def DeleteSlice(self, urn_req):
        self.logger.info("Called DeleteSlice %r" % urn_req)
        if self.slices.has_key(urn_req):
            self.slices.pop(urn_req)
            return True
        self.logger.info('Slice was not found')
        # Slice not found!
        return False

    def ListAggregates(self):
        self.logger.info("Called ListAggregates")
        # TODO: Allow dynamic registration of aggregates
        return self.aggs
    
    def create_slice_gid(self, subject, slice_urn):
        newgid = gid.GID(create=True, subject=SLICE_GID_SUBJ, uuid=gid.create_uuid(), urn=slice_urn)
        keys = cert.Keypair(create=True)
        newgid.set_pubkey(keys)
        issuer_key = cert.Keypair(filename=self.keyfile)
        issuer_cert = gid.GID(filename=self.certfile)
        newgid.set_issuer(issuer_key, cert=issuer_cert)
        newgid.set_parent(issuer_cert)
        newgid.encode()
        newgid.sign()
        return newgid, keys
    
    def CreateUserCredential(self, user_gid):
        self.logger.info("Called CreateUserCredential for GID %s" % gid.GID(string=user_gid).get_hrn())
        ucred = cred.Credential()
        user_gid = gid.GID(string=user_gid)
        ucred.set_gid_caller(user_gid)
        ucred.set_gid_object(user_gid)
        ucred.set_lifetime(USER_CRED_LIFE)
        privileges = rights.determine_rights('user', None)
        ucred.set_privileges(privileges)
        ucred.encode()
        ucred.set_issuer_keys(self.keyfile, self.certfile)
        ucred.sign()
        return ucred.save_to_string()
    
    def create_slice_credential(self, user_gid, slice_gid):
        ucred = cred.Credential()
        ucred.set_gid_caller(user_gid)
        ucred.set_gid_object(slice_gid)
        ucred.set_lifetime(SLICE_CRED_LIFE)
        privileges = rights.determine_rights('slice', None)
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

publicid_urn_prefix = 'urn:publicid:'

def urn_to_publicid(urn):
    # Remove prefix
    if not urn.startswith(publicid_urn_prefix):
        # Erroneous urn for conversion
        raise ValueError('Invalid urn: ' + urn)
    publicid = urn[len(publicid_urn_prefix):]
    for a, b in reversed(publicid_xforms):
        publicid = publicid.replace(b, a)
    return publicid

def publicid_to_urn(id):
    for a, b in publicid_xforms:
        id = id.replace(a, b)
    # prefix with 'urn:publicid:'
    return publicid_urn_prefix + id
