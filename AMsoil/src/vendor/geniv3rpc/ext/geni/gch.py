#----------------------------------------------------------------------
# Copyright (c) 2011-2 Raytheon BBN Technologies
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
Reference GENI GCH Clearinghouse, for talking to the GENI Clearinghouse
via xmlrpc instead of smime (its native interface)
Run from gcf-gch.py
Will produce signed user credentials from a GID, return a
list of aggregates read from a config file, and create a new Slice Credential.
"""

import dateutil.parser
import datetime
import logging
import os
import socket
import traceback
import uuid

from ch import SampleClearinghouseServer
from SecureXMLRPCServer import SecureXMLRPCServer
import geni.util.cred_util as cred_util
from geni.util.ch_interface import *

# FIXME: GENI CH APIs have evolved since this was last run

# Clearinghouse interface that communicates with the 
# new clearinghouse services (SA, PA, MA, CS, AUTHZ, LOG, etc.)
class GENIClearinghouse(object):

    def __init__(self):
        self.logger = logging.getLogger('gcf-gch')

    def runserver(self, addr, keyfile=None, certfile=None,
                  ca_certs=None, config=None):
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

        # This is the arg to _make_server
        ca_certs_onefname = cred_util.CredentialVerifier.getCAsFileFromDir(ca_certs)

        # Set up the URL's to the CH services
        self.establish_ch_interface();

        # Create the xmlrpc server, load the rootkeys and do the ssl thing.
        self._server = self._make_server(addr, keyfile, certfile,
                                         ca_certs_onefname)
        self._server.register_instance(SampleGENIClearinghouseServer(self))
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
        version['gcf-ch_api'] = 2
        return version

    def CreateProject(self, project_name, lead_id, project_purpose):
        self.logger.info("Called CreateProject");
        argsdict = dict(project_name=project_name, 
                        lead_id=lead_id,
                        project_purpose=project_purpose);
        result = invokeCH(self.pa_url, 'create_project', self.logger, 
                          argsdict, self.certfile, self.keyfile);
#        print("CP.RESULT = " + str(result))
        return result

    def CreateSlice(self, slice_name, project_id, owner_id):
        self.logger.info("Called CreateSlice SN " + slice_name + 
                         " PID " + str(project_id));
        project_name = 'Dummy';
        argsdict = dict(slice_name=slice_name,
                        project_id=project_id, 
                        project_name=project_name, 
                        owner_id=owner_id)

        key_and_cert_files = get_inside_cert_and_key(self._server.peercert, \
                                                         self.ma_url, \
                                                         self.logger);
        inside_keyfile = key_and_cert_files['key'];
        inside_certfile = key_and_cert_files['cert'];
#        print("KF = " + inside_keyfile + " CF = " + inside_certfile);

#        print("SA_URL = " + self.sa_url);
        result = invokeCH(self.sa_url, 'create_slice', self.logger, 
                          argsdict, inside_certfile, inside_certfile);
#        print("RES = " + str(result));
        os.unlink(inside_certfile);
        os.unlink(inside_keyfile);
        
        # Don't understand why, but this returns a 'None' output so I need 
        # to fill it in with a ''
        if(result['output'] == None): result['output'] = '';
#        print("CreateSlice RET = " + str(result));
        return result;

    def GetSliceCredential(self, slice_id, cert, slice_urn=None):
        self.logger.info("Called GetSliceCredential (ID=%s URN=%s)", \
                             slice_id, slice_urn)
        key_and_cert_files = get_inside_cert_and_key(self._server.peercert, \
                                                         self.ma_url, \
                                                         self.logger);
        inside_keyfile = key_and_cert_files['key'];
        inside_certfile = key_and_cert_files['cert'];
#        print("KF = " + inside_keyfile + " CF = " + inside_certfile);

        if (slice_urn != None):
            argsdict = dict(slice_urn=slice_urn);
            row = invokeCH(self.sa_url, 'lookup_slice_by_urn', 
                            self.logger, argsdict, 
                            inside_certfile, inside_keyfile);
#            print("Row = " + str(row));
            if (row['code'] != 0):
                return False;
            slice_id = row['value']['slice_id']
#            print "SLICE_ID = " + str(slice_id);

        argsdict = dict(slice_id=slice_id, experimenter_certificate=cert)
        result = invokeCH(self.sa_url, 'get_slice_credential',
                          self.logger, argsdict, inside_certfile, inside_keyfile);
#        print("SC return = " + str(result))
        os.unlink(inside_certfile);
        os.unlink(inside_keyfile);
        return result

    
    def RenewSlice(self, slice_urn, expire_str):
        self.logger.info("Called RenewSlice(%s, %s)", slice_urn, expire_str)
        return True

    def DeleteSlice(self, urn_req):
        self.logger.info("Called DeleteSlice %r" % urn_req)
        return False

    def ListAggregates(self):
        self.logger.info("Called ListAggregates")
        return None
    
    def CreateUserCredential(self, user_gid):
#        print "GID = " + str(user_gid)
        argsdict=dict(experimenter_certificate=user_gid);
        result = invokeCH(self.sa_url, 'get_user_credential', 
                          self.logger, argsdict, self.certfile, self.keyfile);
        if(result['code'] == 0):
            result = result['value']['user_credential'];
#        print "RES = " + str(result)
        return result;

    def establish_ch_interface(self):
        self.sr_url = "https://" + socket.gethostname() + "/sr/sr_controller.php";
#        print("SR_URL = " + self.sr_url);
        self.sa_url = self.get_first_service_of_type(1); # SERVICE_AUTHORITY
        self.pa_url = self.get_first_service_of_type(2); # PROJECT_AUTHORITY
        self.ma_url = self.get_first_service_of_type(3); # MEMBER_AUTHORITY

    def get_first_service_of_type(self, service_type):
        result = invokeCH(self.sr_url, 'get_services_of_type', 
                          self.logger, 
                          dict(service_type=service_type), 
                          self.certfile, self.keyfile);
#        print("GSOT.RESULT = " + str(result))
        if(result['code'] != 0):
            return None
        services = result['value'];
        service = services[0];
        service_url = service['service_url'];
        print("Service of type " + str(service_type) + " = " + service_url);
        return service_url;
        
class SampleGENIClearinghouseServer(object):
    """A sample clearinghouse with barebones functionality."""

    def __init__(self, delegate):
        self._delegate = delegate
        
    def GetVersion(self):
        return self._delegate.GetVersion()

    def CreateProject(self, project_name, lead_id, project_purpose):
        return self._delegate.CreateProject(project_name, 
                                            lead_id, project_purpose);

    def CreateSlice(self, slice_name, project_id, owner_id):
        return self._delegate.CreateSlice(slice_name, project_id, owner_id);
    
    def GetSliceCredential(self, slice_id, cert, slice_urn=None):
        return self._delegate.GetSliceCredential(slice_id, cert, slice_urn);

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


