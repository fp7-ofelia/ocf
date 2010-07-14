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

import base64
import datetime
import logging
import os
import xml.dom.minidom as minidom
import xmlrpclib
import zlib

import dateutil.parser

import gcf.sfa.trust.credential as cred
import gcf.sfa.trust.gid as gid

class CredentialVerifier(object):
    """Utilities to verify signed credentials from a given set of 
    root certificates. Will compare target and source URNs, and privilages.
    See verify and verify_from_strings methods in particular."""

    CATEDCERTSFNAME = 'CATedCACerts.pem'

    @classmethod
    def getCAsFileFromDir(cls, caCerts):
        '''Take a directory of CA certificates and concatenate them into a single
        file suitable for use by the Python SSL library to validate client 
        credentials. Existing file is replaced.'''
        if caCerts is None:
            raise Exception ('Missing caCerts argument')
        if os.path.isfile(os.path.expanduser(caCerts)):
            return caCerts
        if not os.path.isdir(os.path.expanduser(caCerts)):
            raise Exception ('caCerts arg Not a file or a dir: %s' % caCerts)

        logger = logging.getLogger('gam')

        # Now we have a dir of caCerts files
        # For each file in the dir (isfile), concatenate them into a new file
        comboFullPath = os.path.join(caCerts, CredentialVerifier.CATEDCERTSFNAME)

        caFiles = os.listdir(caCerts)
        #logger.debug('Got %d potential caCert files in the dir', len(caFiles))

        outfile = open(comboFullPath, "w")
        okFileCount = 0
        for filename in caFiles:
            filepath = os.path.join(caCerts, filename)
            # Confirm it's a CA file?
            #        if not file.endswith('.pem'):
            #            continue
            if not os.path.isfile(os.path.expanduser(filepath)):
                logger.debug('Skipping non file %s', filepath)
                continue
            if filename == CredentialVerifier.CATEDCERTSFNAME:
                # logger.debug('Skipping previous cated certs file')
                continue
            okFileCount += 1
            logger.info("Adding trusted cert file %s", filename)
            certfile = open(filepath)
            for line in certfile:
                outfile.write(line)
            certfile.close()
        outfile.close()
        if okFileCount == 0:
            sys.exit('Found NO trusted certs in %s!' %  caCerts)
        else:
            logger.info('Combined dir of %d trusted certs %s into file %s for Python SSL support', okFileCount, caCerts, comboFullPath)
        return comboFullPath

    def __init__(self, root_cert_file):
        self.logger = logging.getLogger('cred-verifier')
        if root_cert_file is None:
            raise Exception("Missing Root certs argument")
        elif os.path.isdir(root_cert_file):
            files = os.listdir(root_cert_file)
            self.root_cert_files = []
            for file in files:
                # FIXME: exclude files that arent cert files? The combo cert file?
                if file == CredentialVerifier.CATEDCERTSFNAME:
                    continue
                self.root_cert_files.append(os.path.expanduser(os.path.join(root_cert_file, file)))
            self.logger.info('AM will accept credentials signed by any of %d root certs found in %s: %r' % (len(self.root_cert_files), root_cert_file, self.root_cert_files))
        elif os.path.isfile(root_cert_file):
            self.logger.info('AM will accept credentials signed by the single root cert %s' % root_cert_file)
            self.root_cert_files = [root_cert_file]
        else:
            raise Exception("Couldn't find Root certs in %s" % root_cert_file)

    def verify_from_strings(self, gid_string, cred_strings, target_urn,
                            privileges):
        def make_cred(cred_string):
            return cred.Credential(string=cred_string)
        return self.verify(gid.GID(string=gid_string),
                           map(make_cred, cred_strings),
                           target_urn,
                           privileges)
        
    def verify_source(self, source_gid, credential):
        source_urn = source_gid.get_urn()
        cred_source_urn = credential.get_gid_caller().get_urn()
        #self.logger.debug('Verifying source %r against credential source %r (cred target %s)',
        #              source_urn, cred_source_urn, credential.get_gid_object().get_urn())
        result = (cred_source_urn == source_urn)
        if result:
         #   self.logger.debug('Source URNs match')
            pass
        else:
            self.logger.debug('Source URNs do not match. Source URN %r != credential source URN %r', source_urn, cred_source_urn)
        return result
    
    def verify_target(self, target_urn, credential):
        if not target_urn:
#            self.logger.debug('No target specified, considering it a match.')
            return True
        else:
            cred_target_urn = credential.get_gid_object().get_urn()
           # self.logger.debug('Verifying target %r against credential target %r',
           #               target_urn, cred_target_urn)
            result = target_urn == cred_target_urn
            if result:
            #    self.logger.debug('Target URNs match.')
                pass
            else:
                self.logger.debug('Target URNs do NOT match. Target URN %r != Credential URN %r', target_urn, cred_target_urn)
            return result

    def verify_privileges(self, privileges, credential):
        result = True
        privs = credential.get_privileges()
        for priv in privileges:
            if not privs.can_perform(priv):
                self.logger.debug('Privilege %s not found on credential %s of %s', priv, credential.get_gid_object().get_urn(), credential.get_gid_caller().get_urn())
                result = False
        return result

    def verify(self, gid, credentials, target_urn, privileges):
        self.logger.debug('Verifying privileges')
        result = list()
        failure = ""
        tried_creds = ""
        for cred in credentials:
            if tried_creds != "":
                tried_creds = "%s, %s" % (tried_creds, cred.get_gid_caller().get_urn())
            else:
                tried_creds = cred.get_gid_caller().get_urn()

            if not self.verify_source(gid, cred):
                failure = "Cred %s fails: Source URNs dont match" % cred.get_gid_caller().get_urn()
                continue
            if not self.verify_target(target_urn, cred):
                failure = "Cred %s on %s fails: Target URNs dont match" % (cred.get_gid_caller().get_urn(), cred.get_gid_object().get_urn())
                continue
            if not self.verify_privileges(privileges, cred):
                failure = "Cert %s doesnt have sufficient privileges" % cred.get_gid_caller().get_urn()
                continue

            try:
                if not cred.verify(self.root_cert_files):
                    failure = "Couldn't validate cert %s with known root certs" % cred.get_gid_caller().get_urn()
                    continue
            except Exception, exc:
                failure = "Couldn't validate cert %s with known root certs: %s" % (cred.get_gid_caller().get_urn(), exc)
                self.logger.info(failure)
                continue
            # If got here it verified
            result.append(cred)

        
        if result and result != list():
            return result
        else:
            # We did not find any credential with sufficient privileges
            # Raise an exception.
            fault_code = 'Insufficient privileges'
            fault_string = 'No credential was found with appropriate privileges. Tried %s. Last failure: %s' % (tried_creds, failure)
            self.logger.error(fault_string)
            raise xmlrpclib.Fault(fault_code, fault_string)

