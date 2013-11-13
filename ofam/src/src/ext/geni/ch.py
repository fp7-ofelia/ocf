#----------------------------------------------------------------------
# Copyright (c) 2011-2012 Raytheon BBN Technologies
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
Run from gcf-ch.py
Will produce signed user credentials from a GID, return a
list of aggregates read from a config file, and create a new Slice Credential.

"""

import datetime
import traceback
import uuid
import os

import dateutil.parser
from SecureXMLRPCServer import SecureXMLRPCServer
import geni.util.cred_util as cred_util
import geni.util.cert_util as cert_util
import geni.util.urn_util as urn_util
import sfa.trust.gid as gid


# Substitute eg "openflow//stanford"
# Be sure this matches init-ca.py:CERT_AUTHORITY 
# This is in publicid format
SLICE_AUTHORITY = "geni//gpo//gcf"

# Credential lifetimes in seconds
# Extend slice lifetimes to actually use the resources
USER_CRED_LIFE = 86400
SLICE_CRED_LIFE = 3600

# Make the max life of a slice 30 days (an arbitrary length).
SLICE_MAX_LIFE_SECS = 30 * 24 * 60 * 60

# The list of Aggregates that this Clearinghouse knows about
# should be defined in the gcf_config file in the am_* properties.
# ListResources will refer the client to these aggregates
# Clearinghouse.runserver currently does the register_aggregate_pair
# calls for each row in that file
# but this should be doable dynamically
# Some sample pairs:
# GPOMYPLC = ('urn:publicid:IDN+plc:gpo1+authority+sa',
#             'http://myplc1.gpolab.bbn.com:12348')
# TESTGCFAM = ('urn:publicid:IDN+geni.net:gpo+authority+gcf', 
#              'https://127.0.0.1:8001') 
# OTHERGPOMYPLC = ('urn:publicid:IDN+plc:gpo+authority+site2',
#                    'http://128.89.81.74:12348')
# ELABINELABAM = ('urn:publicid:IDN+elabinelab.geni.emulab.net',
#                 'https://myboss.elabinelab.geni.emulab.net:443/protogeni/xmlrpc/am')

class SampleClearinghouseServer(object):
    """A sample clearinghouse with barebones functionality."""

    def __init__(self, delegate):
        self._delegate = delegate
        
    def GetVersion(self):
        return self._delegate.GetVersion()

    def CreateSlice(self, urn=None):
        return self._delegate.CreateSlice(urn_req=urn)
    
    def RenewSlice(self, urn, expire_str):
        try:
            return self._delegate.RenewSlice(urn, expire_str)
        except:
            self._delegate.logger.error(traceback.format_exc())
            raise

    def DeleteSlice(self, urn):
        return self._delegate.DeleteSlice(urn)

    def ListAggregates(self):
        return self._delegate.ListAggregates()
    
    def CreateUserCredential(self, cert):
        return self._delegate.CreateUserCredential(cert)


class Clearinghouse(object):

    def __init__(self):
        self.logger = cred_util.logging.getLogger('gcf-ch')
        self.slices = {}
        self.aggs = []

    def load_aggregates(self):
        """Loads aggregates from the clearinghouse section of the config file.
        
        In the config section there are keys for each am, am_1, am_2, ..., am_n
        
        The value for each key is the urn and url of the aggregate separated by a comma
           
        Returns True if aggregates were loaded, False otherwise.
        """
        
        for (key, val) in self.config['clearinghouse'].items():
            if not key.startswith('am_'):
                continue
            
            (urn,url) = val.split(',')
            urn = urn.strip()
            url = url.strip()
            if not urn:
                self.logger.warn('Empty URN for aggregate %s in gcf_config' % key)
                continue
            
            if not url:
                self.logger.warn('Empty URL for aggregate %s in gcf_config' % key)
                continue
            if urn in [x for (x, _) in self.aggs]:
                self.logger.warn('Duplicate URN %s in gcf_config' % key)
                continue
            
            self.logger.info("Registering AM %s at %s", urn, url)
            self.aggs.append((urn, url))
            
        
        
        
        
    def runserver(self, addr, keyfile=None, certfile=None,
                  ca_certs=None, authority=None,
                  user_len=None, slice_len=None, config=None):
        """Run the clearinghouse server."""
        # ca_certs is a dir of several certificates for peering
        # If not supplied just use the certfile as the only trusted root
        self.keyfile = keyfile
        self.certfile = certfile

        self.config = config
        
        # Error check the keyfile, certfile all exist
        if keyfile is None or not os.path.isfile(os.path.expanduser(keyfile)):
            raise Exception("Missing CH key file %s" % keyfile)
        if certfile is None or not os.path.isfile(os.path.expanduser(certfile)):
            raise Exception("Missing CH cert file %s" % certfile)

        if ca_certs is None:
            ca_certs = certfile
            self.logger.info("Using only my CH cert as a trusted root cert")

        self.trusted_root_files = cred_util.CredentialVerifier(ca_certs).root_cert_files
            
        if not os.path.exists(os.path.expanduser(ca_certs)):
            raise Exception("Missing CA cert(s): %s" % ca_certs)

        global SLICE_AUTHORITY, USER_CRED_LIFE, SLICE_CRED_LIFE
        SLICE_AUTHORITY = authority
        USER_CRED_LIFE = int(user_len)
        SLICE_CRED_LIFE = int(slice_len)

        # Load up the aggregates
        self.load_aggregates()
        

        # This is the arg to _make_server
        ca_certs_onefname = cred_util.CredentialVerifier.getCAsFileFromDir(ca_certs)

        # This is used below by CreateSlice
        self.ca_cert_fnames = []
        if os.path.isfile(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.expanduser(ca_certs)]
        elif os.path.isdir(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.join(os.path.expanduser(ca_certs), name) for name in os.listdir(os.path.expanduser(ca_certs)) if name != cred_util.CredentialVerifier.CATEDCERTSFNAME]

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

    def _naiveUTC(self, dt):
        """Converts dt to a naive datetime in UTC.

        if 'dt' has a timezone then
        convert to UTC
        strip off timezone (make it "naive" in Python parlance)
        """
        if dt.tzinfo:
            tz_utc = dateutil.tz.tzutc()
            dt = dt.astimezone(tz_utc)
            dt = dt.replace(tzinfo=None)
        return dt

    def GetVersion(self):
        self.logger.info("Called GetVersion")
        version = dict()
        version['gcf-ch_api'] = 1
        return version

    # FIXME: Change that URN to be a name and non-optional
    # Currently gcf-test.py doesnt supply it, and
    # Omni takes a name and constructs a URN to supply
    def CreateSlice(self, urn_req = None):
        self.logger.info("Called CreateSlice URN REQ %r" % urn_req)
        slice_gid = None

        if urn_req and self.slices.has_key(urn_req):
            # If the Slice has expired, treat this as
            # a request to renew
            slice_cred = self.slices[urn_req]
            slice_exp = self._naiveUTC(slice_cred.expiration)
            if slice_exp <= datetime.datetime.utcnow():
                # Need to renew this slice
                self.logger.info("CreateSlice on %r found existing cred that expired at %r - will renew", urn_req, slice_exp)
                slice_gid = slice_cred.get_gid_object()
            else:
                self.logger.debug("Slice cred is still valid at %r until %r - return it", datetime.datetime.utcnow(), slice_exp)
                return slice_cred.save_to_string()
        
        # First ensure we have a slice_urn
        if urn_req:
            # FIXME: Validate urn_req has the right form
            # to be issued by this CH
            if not urn_util.is_valid_urn(urn_req):
                # FIXME: make sure it isnt empty, etc...
                urn = urn_util.publicid_to_urn(urn_req)
            else:
                urn = urn_req
        else:
            # Generate a unique URN for the slice
            # based on this CH location and a UUID

            # Where was the slice created?
            (ipaddr, port) = self._server.socket._sock.getsockname()
            # FIXME: Get public_id start from a properties file
            # Create a unique name for the slice based on uuid
            slice_name = uuid.uuid4().__str__()[4:12]
            public_id = 'IDN %s slice %s//%s:%d' % (SLICE_AUTHORITY, slice_name,
                                                                   ipaddr,
                                                                   port)
            # this func adds the urn:publicid:
            # and converts spaces to +'s, and // to :
            urn = urn_util.publicid_to_urn(public_id)

        # Now create a GID for the slice (signed credential)
        if slice_gid is None:
            try:
                slice_gid = cert_util.create_cert(urn, self.keyfile, self.certfile)[0]
            except Exception, exc:
                self.logger.error("Cant create slice gid for slice urn %s: %s", urn, traceback.format_exc())
                raise Exception("Failed to create slice %s. Cant create slice gid" % urn, exc)

        # Now get the user GID which will have permissions on this slice.
        # Get client x509 cert from the SSL connection
        # It doesnt have the chain but should be signed
        # by this CHs cert, which should also be a trusted
        # root at any federated AM. So everyone can verify it as is.
        # Note that if a user from a different CH (installed
        # as trusted by this CH for some reason) called this method,
        # that user would be used here - and can still get a valid slice
        try:
            user_gid = gid.GID(string=self._server.pem_cert)
        except Exception, exc:
            self.logger.error("CreateSlice failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to create slice %s. Cant get user GID from SSL client certificate." % urn, exc)

        # OK have a user_gid so can get a slice credential
        # authorizing this user on the slice
        try:
            expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=SLICE_CRED_LIFE)
            # add delegatable=True to make this slice delegatable
            slice_cred = self.create_slice_credential(user_gid,
                                                      slice_gid,
                                                      expiration, delegatable=True)
        except Exception, exc:
            self.logger.error('CreateSlice failed to get slice credential for user %r, slice %r: %s', user_gid.get_hrn(), slice_gid.get_hrn(), traceback.format_exc())
            raise Exception('CreateSlice failed to get slice credential for user %r, slice %r' % (user_gid.get_hrn(), slice_gid.get_hrn()), exc)
        self.logger.info('Created slice %r' % (urn))
        
        self.slices[urn] = slice_cred
        
        return slice_cred.save_to_string()
    
    def RenewSlice(self, slice_urn, expire_str):
        self.logger.info("Called RenewSlice(%s, %s)", slice_urn, expire_str)
        if not self.slices.has_key(slice_urn):
            self.logger.warning('Slice %s was not found', slice_urn)
            return False
        try:
            in_expiration = dateutil.parser.parse(expire_str)
            in_expiration = cred_util.naiveUTC(in_expiration)
        except:
            self.logger.warning('Unable to parse date "%s"', expire_str)
            return False
        # Is requested expiration valid? It must be in the future,
        # but not too far into the future.
        now = datetime.datetime.utcnow()
        if in_expiration < now:
            self.logger.warning('Expiration "%s" is in the past.', expire_str)
            return False
        duration = in_expiration - now
        max_duration = datetime.timedelta(seconds=SLICE_MAX_LIFE_SECS)
        if duration > max_duration:
            self.logger.warning('Expiration %s is too far in the future.',
                                expire_str)
            return False
        # Everything checks out, so create a new slice cred and tuck it away.
        user_gid = gid.GID(string=self._server.pem_cert)
        slice_cred = self.slices[slice_urn]
        slice_gid = slice_cred.get_gid_object()
        # if original slice' privileges were all delegatable,
        # make all the privs here delegatable
        # Of course, the correct thing would be to do it priv by priv...
        dgatable = False
        if slice_cred.get_privileges().get_all_delegate():
            dgatable = True
        slice_cred = self.create_slice_credential(user_gid, slice_gid,
                                                  in_expiration, delegatable=dgatable)
        self.logger.info("Slice %s renewed to %s", slice_urn, expire_str)
        self.slices[slice_urn] = slice_cred
        return True

    def DeleteSlice(self, urn_req):
        self.logger.info("Called DeleteSlice %r" % urn_req)
        if self.slices.has_key(urn_req):
            self.slices.pop(urn_req)
            self.logger.info("Deleted slice")
            return True
        self.logger.info('Slice was not found')
        # Slice not found!
        # FIXME: Raise an error so client knows why this failed?
        return False

    def ListAggregates(self):
        self.logger.info("Called ListAggregates")
        # TODO: Allow dynamic registration of aggregates
        return self.aggs
    
    def CreateUserCredential(self, user_gid):
        '''Return string representation of a user credential
        issued by this CH with caller/object this user_gid (string)
        with user privileges'''
        # FIXME: Validate arg - non empty, my user
        user_gid = gid.GID(string=user_gid)
        self.logger.info("Called CreateUserCredential for GID %s" % user_gid.get_hrn())
        expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=USER_CRED_LIFE)
        try:
            ucred = cred_util.create_credential(user_gid, user_gid, expiration, 'user', self.keyfile, self.certfile, self.trusted_root_files)
        except Exception, exc:
            self.logger.error("Failed to create user credential for %s: %s", user_gid.get_hrn(), traceback.format_exc())
            raise Exception("Failed to create user credential for %s" % user_gid.get_hrn(), exc)
        return ucred.save_to_string()
    
    def create_slice_credential(self, user_gid, slice_gid, expiration, delegatable=False):
        '''Create a Slice credential object for this user_gid (object) on given slice gid (object)'''
        # FIXME: Validate the user_gid and slice_gid
        # are my user and slice
        return cred_util.create_credential(user_gid, slice_gid, expiration, 'slice', self.keyfile, self.certfile, self.trusted_root_files, delegatable)

