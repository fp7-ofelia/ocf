#----------------------------------------------------------------------
# Copyright (c) 2011 Raytheon BBN Technologies
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
import uuid as uuidModule
import os

import dateutil.parser
from SecureXMLRPCServer import SecureXMLRPCRequestHandler
import geni.util.cred_util as cred_util
import geni.util.cert_util as cert_util
import geni.util.urn_util as urn_util
import sfa.trust.gid as gid
import sfa.trust.credential
import sfa.util.xrn
from geni.util.ch_interface import *
from ch import Clearinghouse


# Substitute eg "openflow//stanford"
# Be sure this matches init-ca.py:CERT_AUTHORITY 
# This is in publicid format
SLICE_AUTHORITY = "geni//gpo//gcf"

# Credential lifetimes in seconds
# Extend slice lifetimes to actually use the resources
USER_CRED_LIFE = 86400
SLICE_CRED_LIFE = 3600

class PGSAnCHServer(object):
    def __init__(self, delegate, logger):
        self._delegate = delegate
        self.logger = logger

    def GetCredential(self, args=None):
        # all none means return user cred
        # else cred is user cred, id is uuid or urn of object, type=Slice
        #    where omni always uses the urn
        # return is slice credential
        #args: credential, type, uuid, urn
        code = None
        output = None
        value = None
        try:
            value = self._delegate.GetCredential(args)
        except Exception, e:
            output = str(e)
            code = 1 # FIXME: Better codes.
            value = ''
            
        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "Slice or user not found"
        if output is None:
            output = ""
        if code is None:
            code = 0
            
        return dict(code=code, value=value, output=output)

    def Resolve(self, args):
        # Omni uses this, Flack may not need it

        # ID may be a uuid, hrn, or urn
        #   Omni uses hrn for type=User, urn for type=Slice
        # type is Slice or User
        # args: credential, hrn, urn, uuid, type
        # Return is dict:
#When the type is Slice:
#
#{
#  "urn"  : "URN of the slice",
#  "uuid" : "rfc4122 universally unique identifier",
#  "creator_uuid" : "UUID of the user who created the slice",
#  "creator_urn" : "URN of the user who created the slice",
#  "gid"  : "ProtoGENI Identifier (an x509 certificate)",
#  "component_managers" : "List of CM URNs which are known to contain slivers or tickets in this slice. May be stale"
#}
#When the type is User:
#
#{
#  "uid"  : "login (Emulab) ID of the user.",
#  "hrn"  : "Human Readable Name (HRN)",
#  "uuid" : "rfc4122 universally unique identifier",
#  "email": "registered email address",
#  "gid"  : "ProtoGENI Identifier (an x509 certificate)",
#  "name" : "common name",
#}
        code = None
        output = None
        value = None
        try:
            self.logger.debug("Calling resolve in delegate")
            value = self._delegate.Resolve(args)
        except Exception, e:
            output = str(e)
            value = ""
            code = 1 # FIXME: Better codes
            
        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "Slice or user not found"
        if output is None:
            output = ""
        if code is None:
            code = 0
        return dict(code=code, value=value, output=output)

    def Register(self, args):
        # Omni uses this, Flack should not for our purposes
        # args are credential, hrn, urn, type
        # cred is user cred, type must be Slice
        # returns slice cred
        code = None
        output = None
        value = None
        try:
            self.logger.debug("Calling register in delegate")
            value = self._delegate.Register(args)
        except Exception, e:
            output = str(e)
            code = 1 # FIXME: Better codes
            value = ''
            
        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "User not found or couldn't create slice"
        if output is None:
            output = ""
        if code is None:
            code = 0

        return dict(code=code, value=value, output=output)

    def RenewSlice(self, args):
        # Omni uses this, Flack should not for our purposes
        # args are credential, hrn, urn, type
        # cred is user cred, type must be Slice
        # returns slice cred
        code = None
        output = None
        value = None
        try:
            self.logger.debug("Calling register in delegate")
            value = self._delegate.RenewSlice(args)
        except Exception, e:
            output = str(e)
            code = 1 # FIXME: Better codes
            value = ''

        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "User not found or couldn't create slice"
        if output is None:
            output = ""
        if code is None:
            code = 0

        return dict(code=code, value=value, output=output)

# Skipping Remove, DiscoverResources

    def GetKeys(self, args):
        # cred is user cred
        # return list( of dict(type='ssh', key=$key))
        # args: credential
        code = None
        output = None
        value = None
        try:
            value = self._delegate.GetKeys(args)
        except Exception, e:
            output = str(e)
            code = 1 # FIXME: Better codes
            value = ''
            
        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "User not found or couldnt get SSH keys"
        if output is None:
            output = ""
        if code is None:
            code = 0
            
        return dict(code=code, value=value, output=output)

# Skipping BindToSlice, RenewSlice, Shutdown, GetVersion
# =====
# CH API:

# Skipping GetCredential, Register, Resolve, Remove, Shutdown

    def ListComponents(self, args):
        # Returns list of CMs (AMs)
        # cred is user cred or slice cred - Omni uses user cred
        # return list( of dict(gid=<cert>, hrn=<hrn>, url=<AM URL>))
        # Matt seems to say hrn is not critical, and can maybe even skip cert
        # args: credential
        code = None
        output = None
        value = None
        try:
            self.logger.debug("Calling ListComponents(%r)", args)
            value = self._delegate.ListComponents(args)
            self.logger.debug("ListComponents result: %r", value)
        except Exception, e:
            self.logger.error("ListComponents exception: %s", str(e))
            output = str(e)
            code = 1 # FIXME: Better codes
            value = ''
            
        # If the underlying thing is a triple, return it as is
        if isinstance(value, dict) and value.has_key('value'):
            if value.has_key('code'):
                code = value['code']
            if value.has_key('output'):
                output = value['output']
            value = value['value']

        if value is None:
            value = ""
            if code is None or code == 0:
                code = 1
            if output is None:
                output = "User not found or couldnt list AMs"
        if output is None:
            output = ""
        if code is None:
            code = 0

        self.logger.debug("ListComponents final code: %r", code)
        self.logger.debug("ListComponents final value: %r", value)
        self.logger.debug("ListComponents final output: %r", output)
        return dict(code=code, value=value, output=output)

# Skipping PostCRL, List, GetVersion

# Flack wants to communicate to its Clearinghouse via the HTTP path
# "/ch".  By default our XML-RPC server only handles requests to "/"
# (and "/RPC2" according to the documentation). This class modifies
# the acceptable RPC paths to include "/". I chose to eliminate
# "/RPC2" from the list because we don't use it.
#
# This class is used when the XML-RPC server is instantiated. After
# instantiation, the server object is modified to use this request
# handler instead of our default handler (SecureXMLRPCRequestHandler).
#
# See http://docs.python.org/2/library/simplexmlrpcserver.html
class PgChRequestHandler(SecureXMLRPCRequestHandler):
    rpc_paths = ('/', '/ch',)

class PGClearinghouse(Clearinghouse):

    def __init__(self, gcf=False):
        Clearinghouse.__init__(self)
        self.logger = cred_util.logging.getLogger('gcf-pgch')
        self.gcf=gcf
        # Cache inside keys for users.
        self.inside_keys = dict()

    def loadURLs(self):
        for (key, val) in self.config['clearinghouse'].items():
            if key.lower() == 'sa_url':
                self.sa_url = val.strip()
                continue
            if key.lower() == 'ma_url':
                self.ma_url = val.strip()
                continue
            if key.lower() == 'sr_url':
                self.sr_url = val.strip()
                continue
            if key.lower() == 'pa_url':
                self.pa_url = val.strip()
                continue
        
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
        if keyfile is None or not os.path.isfile(os.path.expanduser(keyfile)) or os.path.getsize(os.path.expanduser(keyfile)) < 1:
            raise Exception("Missing CH key file %s" % keyfile)
        if certfile is None or not os.path.isfile(os.path.expanduser(certfile)) or os.path.getsize(os.path.expanduser(certfile)) < 1:
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
        
        # load up URLs for things we proxy for
        self.loadURLs()

        self.macert = ''
        if self.config['clearinghouse'].has_key('macert_path'):
            self.macert = self.config['clearinghouse']['macert_path']

        # This is the arg to _make_server
        ca_certs_onefname = cred_util.CredentialVerifier.getCAsFileFromDir(ca_certs)

        # This is used below by CreateSlice
        self.ca_cert_fnames = []
        if os.path.isfile(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.expanduser(ca_certs)]
        elif os.path.isdir(os.path.expanduser(ca_certs)):
            self.ca_cert_fnames = [os.path.join(os.path.expanduser(ca_certs), name) for name in os.listdir(os.path.expanduser(ca_certs)) if name != cred_util.CredentialVerifier.CATEDCERTSFNAME]

        self.trusted_roots = []
        for fname in self.ca_cert_fnames:
            try:
                self.trusted_roots.append(gid.GID(filename=fname))
            except Exception, exc:
                self.logger.error("Failed to load trusted root cert from %s: %s", fname, exc)

        self._cred_verifier = cred_util.CredentialVerifier(ca_certs)

        # Create the xmlrpc server, load the rootkeys and do the ssl thing.
        self._server = self._make_server(addr, keyfile, certfile,
                                         ca_certs_onefname)
        # Override the default RequestHandlerClass to allow
        # Flack to communicate to our PGCH using either "/"
        # or "/ch" for SA or CH respectively.
        self._server.RequestHandlerClass = PgChRequestHandler
        self._server.register_instance(PGSAnCHServer(self, self.logger))
        self.logger.info('GENI PGCH Listening on port %d...' % (addr[1]))
        self._server.serve_forever()

    def readfile(self, path):
        f = open(path)
        x = f.read()
        f.close()
        return x

    def split_chain(self, chain):
        x = chain.split('\n')
        sep = '-----END CERTIFICATE-----'
        out = list()
        while x.count(sep):
            pos = x.index(sep)
            out.append("\n".join(x[0:pos+1]))
            x = x[pos+1:]
        return out

    def getInsideKeys(self, uuid):
        if self.inside_keys.has_key(uuid):
            return self.inside_keys[uuid]
        # Fetch the inside keys...
        self.logger.info("get inside keys for %r", uuid);
        argsdict = dict(member_id=uuid)
        portalKey = self.readfile('/usr/share/geni-ch/portal/portal-key.pem')
        portalCert = self.readfile('/usr/share/geni-ch/portal/portal-cert.pem')
        triple = invokeCH(self.ma_url, "lookup_keys_and_certs", self.logger,
                          argsdict,
                          # Temporarily hardcode authority keys to get
                          # the user's inside keys
                          [portalCert], portalKey)
        if triple['code'] != 0:
            self.logger.error("Failed to get inside keys for %s: %s",
                              uuid,
                              triple['output'])
            return None
        keysdict = triple['value']
        inside_key = keysdict['private_key']
        inside_certs = self.split_chain(keysdict['certificate'])
        result = (inside_key, inside_certs)
        # Put it in the cache
        self.inside_keys[uuid] = result
        return result

    def GetCredential(self, args=None):
        #args: credential, type, uuid, urn
        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']
        type = None
        if args and args.has_key('type'):
            type = args['type']
        urn = None
        if args and args.has_key('urn'):
            urn = args['urn']
        uuid = None
        if args and args.has_key('uuid'):
            uuid = args['uuid']
        self.logger.debug("In getCred")
        
        # Construct cert, pulling in the intermediate signer cert if any (SSL doesn't give us the chain)
        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)

        # Construct the GID
        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)

        self.logger.debug("Constructed user_gid")

        # Validate the GID is trusted by our roots
        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
            raise

        if credential is None:
            # return user credential

            if self.gcf:
                return self.CreateUserCredential(user_certstr)
            else:
                # follow make_user_credential in sa/php/sa_utils?
                # get_user_credential(experimenter_certificate=exp_cert)
                self.logger.debug("About to send exp cert with just %s " % user_certstr)
                argsdict=dict(experimenter_certificate=user_certstr)
                restriple = None
                try:
                    # CAUTION: untested use of inside cert/key
                    user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                    inside_key, inside_certs = self.getInsideKeys(user_uuid)
                    restriple = invokeCH(self.sa_url, "get_user_credential",
                                         self.logger, argsdict, inside_certs,
                                         inside_key)
                except Exception, e:
                    self.logger.error("GetCred exception invoking get_user_credential: %s", e)
                    raise
                getValueFromTriple(restriple, self.logger, "get_user_credential")
                if restriple["code"] != 0:
                    self.logger.error("GetCred got error getting from get_user_credential. Code: %d, Msg: %s", restriple["code"], restriple["output"])
                    return restriple
                
                res = getValueFromTriple(restriple, self.logger, "get_user_credential", unwrap=True)
                #self.logger.info("Got res from get_user_cred: %s", res)
                if res and res.has_key("user_credential") and res["user_credential"].strip() != '':
                    return res["user_credential"]
                else:
                    self.logger.error("GetCred got result not array or no user_credential: %s", res)
                    raise Exception("GetCred got result not array or no user_credential: %s" % res)

        if not type or type.lower() != 'slice':
            self.logger.error("Expected type of slice, got %s", type)

        # id is urn or uuid
        if not urn and not uuid:
            raise Exception("Missing ID for slice to get credential for")
        if urn and not urn_util.is_valid_urn(urn):
            self.logger.error("URN not a valid URN: %s", urn)
            # Confirm it is a valid UUID
            raise Exception("Given invalid URN to look up slice %s. Look up slice by UUID?" % urn)

        if uuid:
            # Check a valid UUID
            try:
                uuidO = uuidModule.UUID(uuid)
            except:
                self.logger.error("Invalid uuid in GetCredential: %s", uuid)
                if not self.gcf and urn:
                    # For non GCF if we have a URN, use that
                    uuid = None

            # look up by uuid
            if self.gcf:
                raise Exception("Got UUID in GetCredential - unsupported")

        if self.gcf:
            # For now, do this as a createslice
            return self.CreateSlice(urn)

        # Validate user credential
        creds = list()
        creds.append(credential)
        privs = ()
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)

        # Need the slice_id given the urn
        # need the client cert
        # lookup_slice with arg slice_urn
        if not uuid:
            argsdict=dict(slice_urn=urn)
            slicetriple = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                slicetriple = invokeCH(self.sa_url, 'lookup_slice_by_urn',
                                       self.logger, argsdict, inside_certs,
                                       inside_key)
            except Exception, e:
                self.logger.error("Exception doing lookup_slice: %s" % e)
                raise
            sliceval = getValueFromTriple(slicetriple, self.logger, "lookup_slice to get slice cred")
            if sliceval and sliceval.has_key("code") and sliceval["code"] == 0 and sliceval.has_key("value") and sliceval["value"]:
                sliceval = sliceval["value"]
            else:
                self.logger.info("Found no slice by urn %s" % urn)
                return sliceval

            if not sliceval or not sliceval.has_key('slice_id'):
                self.logger.error("malformed slice value from lookup_slice: %s" % sliceval)
                raise Exception("malformed sliceval from lookup_slice")
            slice_id=sliceval['slice_id']
            self.logger.info("Found slice id %s for urn %s", slice_id, urn)
        else:
            slice_id = uuid
        argsdict = dict(experimenter_certificate=user_certstr, slice_id=slice_id)
        res = None
        try:
            user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
            inside_key, inside_certs = self.getInsideKeys(user_uuid)
            res = invokeCH(self.sa_url, 'get_slice_credential', self.logger,
                           argsdict, inside_certs, inside_key)
        except Exception, e:
            self.logger.error("Exception doing get_slice_cred: %s" % e)
            raise
        getValueFromTriple(res, self.logger, "get_slice_credential")
        if not res['value']:
            return res
        if not isinstance(res['value'], dict) and res['value'].has_key('slice_credential'):
            return res
        return res['value']['slice_credential']

    def Resolve(self, args):
        # args: credential, hrn, urn, uuid, type
        # ID may be a uuid, hrn, or urn
        #   Omni uses hrn for type=User, urn for type=Slice
        # type is Slice or User
        # Return is dict: (see above)

        # Get full user cert chain (append MA if any)
        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)

        # Construct GID
        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)

        # Validate GID
        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
            raise

        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']
        type = None
        if args and args.has_key('type'):
            type = args['type']
        urn = None
        if args and args.has_key('urn'):
            urn = args['urn']
        hrn = None
        if args and args.has_key('hrn'):
            hrn = args['hrn']
        uuid = None
        if args and args.has_key('uuid'):
            uuid = args['uuid']

        if credential is None:
            raise Exception("Resolve missing credential")

        # Validate user credential
        creds = list()
        creds.append(credential)
        privs = ()
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)

        # confirm type is Slice or User
        if not type:
            self.logger.error("Missing type to Resolve")
            raise Exception("Missing type to Resolve")
        if type.lower() == 'slice':
            # type is slice

            if hrn and (not urn or not urn_util.is_valid_urn(urn)):
                # Convert hrn to urn
                urn = sfa.util.xrn.hrn_to_urn(hrn, "slice")
                self.logger.debug("Made slice urn %s from hrn %s", urn, hrn)
                #raise Exception("We don't handle hrn inputs")

            if not urn or not urn_util.is_valid_urn(urn):
                self.logger.error("Didnt get a valid URN for slice in resolve: %s", urn)
                if uuid:
                    self.logger.error("Got a UUID instead? %s" % uuid)
                    try:
                        uuidO = uuidModule.UUID(uuid)
                    except:
                        self.logger.error("Resolve(slice): Invalid UUID %s", uuid)
                        raise Exception("Resolve(slice): No valid URN (even using hrn) and no valid UUID")
                        # FIXME: then what?

                    # FIXME For gcf, could loop over all slices, extract uuid, and compare
                    if self.gcf:
                        raise Exception("Didnt get a valid URN for slice in resolve: %s", urn)

            if self.gcf:
                # FIXME: Handle uuid input
                # For type slice, error means no known slice. Else the slice exists.
                if self.slices.has_key(urn):
                    slice_cred = self.slices[urn]
                    slice_cert = slice_cred.get_gid_object()
                    slice_uuid = ""
                    try:
                        slice_uuid = str(uuidModule.UUID(int=slice_cert.get_uuid()))
                    except Exception, e:
                        self.logger.error("Failed to get a UUID from slice cert: %s", e)
                    owner_cert = slice_cred.get_gid_caller()
                    owner_urn = owner_cert.get_urn()
                    owner_uuid = ""
                    try:
                        owner_uuid = str(uuidModule.UUID(int=owner_cert.get_uuid()))
                    except Exception, e:
                        self.logger.error("Failed to get a UUID from user cert: %s", e)
                    return dict(urn=urn, uuid=slice_uuid, creator_uuid=owner_uuid, creator_urn=owner_urn, gid=slice_cred.get_gid_object().save_to_string(), component_managers=list())
#{
#  "urn"  : "URN of the slice",
#  "uuid" : "rfc4122 universally unique identifier",
#  "creator_uuid" : "UUID of the user who created the slice",
#  "creator_urn" : "URN of the user who created the slice",
#  "gid"  : "ProtoGENI Identifier (an x509 certificate)",
#  "component_managers" : "List of CM URNs which are known to contain slivers or tickets in this slice. May be stale"
#}
                else:
                    raise Exception("No such slice %s locally" % urn)
            else:
                # Call the real CH
                if urn and not uuid:
                    argsdict=dict(slice_urn=urn)
                    op = 'lookup_slice_by_urn'
                else:
                    argsdict=dict(slice_id=uuid)
                    op = 'lookup_slice'
                slicetriple = None
                try:
                    # CAUTION: untested use of inside cert/key
                    user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                    inside_key, inside_certs = self.getInsideKeys(user_uuid)
                    slicetriple = invokeCH(self.sa_url, op, self.logger,
                                           argsdict, inside_certs, inside_key)
                except Exception, e:
                    self.logger.error("Exception doing lookup_slice: %s" % e)
                    raise
                # FIXME: What do we return if there is no such slice?
                sliceval = getValueFromTriple(slicetriple, self.logger, "lookup_slice to get slice cred")
                if sliceval and sliceval.has_key("code") and sliceval["code"] == 0 and sliceval.has_key("value") and sliceval["value"]:
                    sliceval = sliceval["value"]
                else:
                    self.logger.info("Found no slice by urn %s" % urn)
                    return sliceval

                if not sliceval or not sliceval.has_key('slice_id'):
                    self.logger.error("malformed slice value from lookup_slice: %s" % sliceval)
                    raise Exception("malformed sliceval from lookup_slice")
#{
#  "urn"  : "URN of the slice",
#  "uuid" : "rfc4122 universally unique identifier",
#  "creator_uuid" : "UUID of the user who created the slice",
#  "creator_urn" : "URN of the user who created the slice",
#  "gid"  : "ProtoGENI Identifier (an x509 certificate)",
#  "component_managers" : "List of CM URNs which are known to contain slivers or tickets in this slice. May be stale"
#}
                # Got back slice_id, slice_name, project_id, expiration, owner_id, slice_email, certificate, slice_urn
                # slice_id = slice_uuid
                # owner_id == creator_uuid (for now)
                # certificate = gid
                # creator urn is harder - need to ask the MA I think
                return dict(urn=urn, uuid=sliceval['slice_id'], creator_uuid=sliceval['owner_id'], creator_urn='', gid=sliceval['certificate'], component_managers=list())

        elif type.lower() == 'user':
            # type is user
            # To date, this is only used for ListMySlices - given an hrn, return slice names. But the PG API
            # returns other stuff as well

            uuidO = None
            # This should be an hrn. Maybe handle others?

            # turn an hrn into a urn
            if hrn and (not urn or not urn_util.is_valid_urn(urn)):
                urn = sfa.util.xrn.hrn_to_urn(hrn, "user")
                self.logger.debug("Made user urn %s from hrn %s", urn, hrn)
            if not urn or not urn_util.is_valid_urn(urn):
                self.logger.error("Didnt get a valid URN for user in resolve: %s", urn)

            # Validate uuid
            if uuid:
                self.logger.error("Got a UUID instead? %s" % uuid)
                try:
                    uuidO = uuidModule.UUID(uuid)
                except:
                    self.logger.error("Resolve(user): Invalid UUID %s", uuid)

            # If no urn and no valid UUID, give up
            if (not urn or not urn_util.is_valid_urn(urn)) and not uuidO:
                raise Exception("Resolve(user): No valid URN (even using hrn) and no valid UUID")

            # Handle GCF mode: input is a URN, output is a list of URNs that we'll convert
            if self.gcf:
                if uuidO and (not urn or not urn_util.is_valid_urn(urn)):
                    # If uuid matches the caller uuid, then pull out the URN from the caller cert
                    client_uuidO = uuidModule.UUID(int=user_gid.get_uuid())
                    if uuidO.int == client_uuidO.int:
                        urn = user_gid.get_urn()
                # If we still have no URN, bail
                if not urn or not urn_util.is_valid_urn(urn):
                    self.logger.warn("Resolve(user) on gcf implemented only when given a urn or can construct on. Was asked about user with hrn=%s (or urn=%s, uuid=%s)" % (hrn, urn, uuid))
                    return dict(slices=list())

                # OK, we have a URN
                slices = self.ListMySlices(urn)
                # This is a list of URNs. I want names, and keyed by slices=
                slicenames = list()
                for slice in slices:
                    slicenames.append(urn_util.nameFromURN(slice))
                return dict(slices=slicenames)

            else:
                # Talking to the real CH. Need a uuid, from which we can get a lot of data about slices
                # for which that uuid is a member.

                # If we have a uuid, we can look up the user with that
                # Else, try to match the urn with the subjectAltName in the client cert,
                # and get the UUID from there
                if not uuidO and urn and urn_util.is_valid_urn(urn):
                    client_uuidO = uuidModule.UUID(int=user_gid.get_uuid())
                    client_urn = user_gid.get_urn()
                    if urn == client_urn:
                        self.logger.debug("Client urn matches query URN. Get UUID that way")
                        uuidO = client_uuidO

                if not uuidO:
                    self.logger.warn("Resolve(user) implemented only when given a uuid or the hrn/urn of the client making the query. Was asked about user with hrn=%s (or urn=%s, uuid=%s)" % (hrn, urn, uuid))
                    return dict(slices=list())

                # Query the SA for a list of slices that this UUID is a member of
                # call is lookup_slices(sa_url, signer, None, uuidO)
                # that returns 
                # code/value/output triple
                # value is a list of arrays: 'slice_id', 'slice_name', 'project_id', 'expiration', ....
                argsdict = dict(project_id=None,member_id=str(uuidO))
                self.logger.debug("Doing lookup_slices on project_id=None, member_id=%s", str(uuidO))
                try:
                    # CAUTION: untested use of inside cert/key
                    inside_key, inside_certs = self.getInsideKeys(str(uuidO))
                    slicestriple = invokeCH(self.sa_url, "lookup_slices",
                                            self.logger, argsdict, inside_certs,
                                            inside_key)
                except Exception, e:
                    self.logger.error("Exception getting slices for member %s: %s", str(uuidO), e)
                    raise

                # If there was an error, return it
                getValueFromTriple(slicestriple, self.logger, "lookup_slices")
                if slicestriple["code"] != 0:
                    self.logger.error("Resolve got error getting from lookup_slices. Code: %d, Msg: %s", slicestriple["code"], slicestriple["output"])
                    return slicestriple

                # otherwise, create a list of the slice_name fields, and return that
                slices = getValueFromTriple(slicestriple, self.logger, "lookup_slices", unwrap=True)
                slicenames = list()
                if slices:
                    if isinstance(slices, list):
                        for slice in slices:
                            if isinstance(slice, dict) and slice.has_key('slice_name'):
                                slicenames.append(slice['slice_name'])
                            else:
                                self.logger.error("Malformed entry in list of slices from lookup_slices: %r", slice)
                    else:
                        self.logger.error("Malformed value (not a list) from lookup_slices: %r", slices)
                return dict(slices=slicenames)

        else:
            self.logger.error("Unknown type %s" % type)
            raise Exception("Unknown type %s" % type)

    def Register(self, args):
        # Omni uses this, Flack should not for our purposes
        # args are credential, hrn, urn, type
        # cred is user cred, type must be Slice
        # returns slice cred

        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)

        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)

        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
            raise

        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']
        type = None
        if args and args.has_key('type'):
            type = args['type']
        urn = None
        if args and args.has_key('urn'):
            urn = args['urn']
        hrn = None
        if args and args.has_key('hrn'):
            hrn = args['hrn']

        if credential is None:
            raise Exception("Register missing credential")

        # Validate user credential
        creds = list()
        creds.append(credential)
        privs = ()
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)

        # confirm type is Slice or User
        if not type:
            self.logger.error("Missing type to Resolve")
            raise Exception("Missing type to Resolve")
        if not type.lower() == 'slice':
            self.logger.error("Tried to register type %s" % type)
            raise Exception("Can't register non slice %s" % type)

        if not urn and hrn is not None:
            # Convert hrn to urn
            urn = sfa.util.xrn.hrn_to_urn(hrn, "slice")
            #raise Exception("hrn to Register not supported")

        if not urn or not urn_util.is_valid_urn(urn):
            raise Exception("invalid slice urn to create: %s" % urn)

        if self.gcf:
            return self.CreateSlice(urn)
        else:
            # Infer owner_id from current user's cert and uuid in there
            # pull out slice name from urn
            # but what about project_id? look for something after authority before +authority+?
            try:
                owner_id = str(uuidModule.UUID(int=user_gid.get_uuid()))
            except Exception, e:
                self.logger.error("Register(urn=%s): Failed to find owner account ID from UUID in user cert: %s", urn, e)
                raise
            sUrn = urn_util.URN(urn=urn)
            slice_name = sUrn.getName()
            slice_auth = sUrn.getAuthority()
            # Compare that with SLICE_AUTHORITY
            project_id = ''
            if slice_auth and slice_auth.startswith(SLICE_AUTHORITY) and len(slice_auth) > len(SLICE_AUTHORITY)+1:
                project_name = slice_auth[len(SLICE_AUTHORITY)+2:]
                self.logger.info("Creating slice in project %s" % project_name)
                if project_name.strip() == '':
                    self.logger.warn("Empty project name will fail")
                argsdict = dict(project_name=project_name)
                projtriple = None
                try:
                    # CAUTION: untested use of inside cert/key
                    user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                    inside_key, inside_certs = self.getInsideKeys(user_uuid)
                    projtriple = invokeCH(self.pa_url, "lookup_project",
                                          self.logger, argsdict, inside_certs,
                                          inside_key)
                except Exception, e:
                    self.logger.error("Exception getting project of name %s: %s", project_name, e)
                    #raise
                if projtriple:
                    projval = getValueFromTriple(projtriple, self.logger, "lookup_project for create_slice", unwrap=True)
                    project_id = projval['project_id']
            argsdict = dict(project_id=project_id, slice_name=slice_name, owner_id=owner_id, project_name=project_name)
            slicetriple = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                slicetriple = invokeCH(self.sa_url, "create_slice", self.logger,
                                       argsdict, inside_certs, inside_key)
            except Exception, e:
                self.logger.error("Exception creating slice %s: %s" % (urn, e))
                raise

            # Will raise an exception if triple malformed
            slicetriple = getValueFromTriple(slicetriple, self.logger, "create_slice")
            if not slicetriple['value']:
                self.logger.error("No slice created. Return the triple with the error")
                return slicetriple
            if slicetriple['code'] != 0:
                self.logger.error("Return code != 0. Return the triple")
                return slicetriple
            sliceval = getValueFromTriple(slicetriple, self.logger, "create_slice", unwrap=True)

            # OK, this gives us the info about the slice.
            # Now though we need the slice credential
            argsdict = dict(experimenter_certificate=user_certstr, slice_id=sliceval['slice_id'])
            res = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                res = invokeCH(self.sa_url, 'get_slice_credential', self.logger,
                               argsdict, inside_certs, inside_key)
            except Exception, e:
                self.logger.error("Exception doing get_slice_cred after create_slice: %s" % e)
                raise
            getValueFromTriple(res, self.logger, "get_slice_credential after create_slice")
            if not res['value']:
                return res
            if not isinstance(res['value'], dict) and res['value'].has_key('slice_credential'):
                return res
            return res['value']['slice_credential']

    def RenewSlice(self, args):
        # args are credential, expiration
        # cred is user cred
        # returns renewed slice credential

        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)
        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("RenewSlice failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to RenewSlice. Cant get user GID from SSL client certificate." % exc)

        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("RenewSlice got unverifiable experimenter cert: %s", exc)
            raise

        expiration = None
        if args and args.has_key('expiration'):
            expiration = args['expiration']

        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']

        if credential is None:
            self.logger.error("RenewSlice has no slice credential in its arguments")
            raise Exception("RenewSlice has no slice credential in its arguments")

        # Validate slice credential
        creds = list()
        creds.append(credential)
        privs = ()
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)

        # get Slice UUID (aka slice_id)
        slice_cert = sfa.trust.credential.Credential(string=credential).get_gid_object()
        try:
            slice_uuid = str(uuidModule.UUID(int=slice_cert.get_uuid()))
            self.logger.error("Got UUID from slice cert: %s", slice_uuid)
        except Exception, e:
            self.logger.error("Failed to get a UUID from slice cert: %s", e)

        if self.gcf:
            # Pull urn from slice credential
            urn = sfa.trust.credential.Credential(string=credential).get_gid_object().get_urn()            
            if self.RenewSlice(urn, expiration):
                # return the new slice credential
                return self.slices[urn]
            else:
                # error
                raise "Failed to renew slice %s until %s" % (urn, expiration)
        else:
            argsdict = dict(slice_id=slice_uuid,expiration=expiration)#HEREHERE
            slicetriple = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                slicetriple = invokeCH(self.sa_url, "renew_slice", self.logger,
                                       argsdict, inside_certs, inside_key)
            except Exception, e:
                self.logger.error("Exception renewing slice %s: %s" % (urn, e))
                raise

            # Will raise an exception if triple malformed
            slicetriple = getValueFromTriple(slicetriple, self.logger, "renew_slice")
            if not slicetriple['value']:
                self.logger.error("No slice renewed. Return the triple with the error")
                return slicetriple
            if slicetriple['code'] != 0:
                self.logger.error("Return code != 0. Return the triple")
                return slicetriple
            sliceval = getValueFromTriple(slicetriple, self.logger, "renew_slice", unwrap=True)

            # OK, this gives us the info about the slice.
            # Now though we need the _updated_ slice credential
            argsdict = dict(experimenter_certificate=user_certstr, slice_id=sliceval['slice_id'])
            res = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                res = invokeCH(self.sa_url, 'get_slice_credential', self.logger,
                               argsdict, inside_certs, inside_key)
            except Exception, e:
                self.logger.error("Exception doing get_slice_cred after create_slice: %s" % e)
                raise
            getValueFromTriple(res, self.logger, "get_slice_credential after create_slice")
            if not res['value']:
                return res
            if not isinstance(res['value'], dict) and res['value'].has_key('slice_credential'):
                return res
            return res['value']['slice_credential']

    def GetKeys(self, args):
        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']
        # cred is user cred
        # return list( of dict(type='ssh', key=$key))

        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)

        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)

        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
            raise

        if credential is None:
            raise Exception("Resolve missing credential")

#        self.logger.info("in delegate getkeys about to do cred verify")
        # Validate user credential
        creds = list()
        creds.append(credential)
        privs = ()
#        self.logger.info("type of credential: %s. Type of creds: %s", type(credential), type(creds))
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)
#        self.logger.info("getkeys did cred verify")
        # With the real CH, the SSH keys are held by the portal, not the CH
        # see db-util.php#fetchSshKeys which queries the ssh_key table in the portal DB
        # it takes an account_id
        try:
            user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
        except:
            self.logger.error("GetKeys Failed to find user account ID from cert")
            raise
        user_urn = user_gid.get_urn()
        if not user_uuid:
            self.logger.warn("GetKeys couldnt get uuid for user from cert with urn %s" % user_urn)
        else:
            self.logger.info("GetKeys called for user with uuid %s" % user_uuid)
        # Use new MA lookup_ssh_keys method
        inside_key, inside_certs = self.getInsideKeys(user_uuid)
        argsdict=dict(member_id=user_uuid);
        keys_triple=invokeCH(self.ma_url, "lookup_ssh_keys", self.logger,
                             argsdict, inside_certs, inside_key)
        self.logger.info("lookup_ssh_keys: " + str(keys_triple));
        if not keys_triple['value']:
            self.logger.error("No SSH key structure. Return the triple with error");
            return keys_triple;
        if keys_triple['code'] != 0:
            self.logger.error("Error extracting SSH keys");
            return keys_triple;

        keys = keys_triple['value'];
        if (len(keys) == 0):
            self.logger.error("No SSH keys found");
            return keys;
        ret = list();
        for key in keys:
            ssh_key = key['public_key'];
            entry = dict(type='ssh',
                         key=ssh_key);
            self.logger.info("KEYS = %r", entry);
            ret.append(entry);
        return ret

    def ListComponents(self, args):
        credential = None
        if args and args.has_key('credential'):
            credential = args['credential']
        # Returns list of CMs (AMs)
        # cred is user cred or slice cred - Omni uses user cred
        # return list( of dict(gid=<cert>, hrn=<hrn>, url=<AM URL>))
        # Matt seems to say hrn is not critical, and can maybe even skip cert

        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)

        try:
            user_gid = gid.GID(string=user_certstr)
        except Exception, exc:
            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)

        try:
            user_gid.verify_chain(self.trusted_roots)
        except Exception, exc:
            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
            raise

        if credential is None:
            raise Exception("Resolve missing credential")

        # Validate user credential
        creds = list()
        creds.append(credential)
        privs = ()
        self._cred_verifier.verify_from_strings(user_certstr, creds, None, privs)

        if self.gcf:
            ret = list()
            for (urn, url) in self.aggs:
                # convert urn to hrn
                hrn = sfa.util.xrn.urn_to_hrn(urn)
                ret.append(dict(gid='amcert', hrn=hrn, url=url, urn=urn))
            return ret
        else:
            argsdict = dict(service_type=0)
            amstriple = None
            try:
                # CAUTION: untested use of inside cert/key
                user_uuid = str(uuidModule.UUID(int=user_gid.get_uuid()))
                inside_key, inside_certs = self.getInsideKeys(user_uuid)
                amstriple = invokeCH(self.sr_url, "get_services_of_type",
                                     self.logger, argsdict, inside_certs,
                                     inside_key)
            except Exception, e:
                self.logger.error("Exception looking up AMs at SR: %s", e)
                raise
            self.logger.debug("Got list of ams: %s", amstriple)
            if amstriple and amstriple.has_key("value") and amstriple["value"]:
                amstriple = getValueFromTriple(amstriple, self.logger, "get_services_of_type(AM)", unwrap=True)
            else:
                return getValueFromTriple(amstriple, self.logger, "get_services_of_type(AM)")
            ret = list()
            if amstriple:
                for am in amstriple:
                    gidS=am['service_cert_contents']
                    url=am['service_url']
                    if url is None or url.strip() == '':
                        self.logger.error("Empty url for returned AM Service %s" % am['service_name'])
                        url = ''
                    gidO = None
                    hrn = 'AM-hrn-unknown'
                    urn = 'AM-urn-unknown'
                    if gidS and gidS.strip() != '':
                        self.logger.debug("Got AM cert for url %s:\n%s", url, gidS)
                        try:
                            gidO = gid.GID(string=gidS)
                            urnC = gidO.get_urn()
                            if urnC and urnC.strip() != '':
                                urn = urnC
                                hrn = sfa.util.xrn.urn_to_hrn(urn)
                        except Exception, exc:
                            self.logger.error("ListComponents failed to create AM gid for AM at %s from server_cert we got from server: %s", url, traceback.format_exc())
                    else:
                        gidS = ''
                    # try except construct gidO. Then pull out URN. Then turn that into hrn
                    ret.append(dict(gid=gidS, hrn=hrn, url=url, urn=urn))
            return ret

# End of implementation of PG CH/SA servers
# ==========================

    def GetVersion(self):
        self.logger.info("Called GetVersion")
        version = dict()
        version['gcf-pgch_api'] = 1
        return version

# Rest comes from parent class

# ===========================

