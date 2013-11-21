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
'''
Credential creation and verification utilities.
'''

import os
import logging
import xmlrpclib
import sys
import datetime
import dateutil

import sfa.trust.credential as cred
import sfa.trust.gid as gid
import sfa.trust.rights as rights
from sfa.util.xrn import hrn_authfor_hrn

def naiveUTC(dt):
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

class CredentialVerifier(object):
    """Utilities to verify signed credentials from a given set of 
    root certificates. Will compare target and source URNs, and privileges.
    See verify and verify_from_strings methods in particular."""

    CATEDCERTSFNAME = 'CATedCACerts.pem'


    # root_cert_file is a trusted root file file or directory of 
    # trusted roots for verifying credentials
    def __init__(self, root_cert_fileordir):
        self.logger = logging.getLogger('cred-verifier')
        if root_cert_fileordir is None:
            raise Exception("Missing Root certs argument")
        elif os.path.isdir(root_cert_fileordir):
            files = os.listdir(root_cert_fileordir)
            self.root_cert_files = []
            for file in files:
                # FIXME: exclude files that aren't cert files? The combo cert file?
                if file == CredentialVerifier.CATEDCERTSFNAME:
                    continue
                self.root_cert_files.append(os.path.expanduser(os.path.join(root_cert_fileordir, file)))
            self.logger.info('Will accept credentials signed by any of %d root certs found in %s: %r' % (len(self.root_cert_files), root_cert_fileordir, self.root_cert_files))
        elif os.path.isfile(root_cert_fileordir):
            self.logger.info('Will accept credentials signed by the single root cert %s' % root_cert_fileordir)
            self.root_cert_files = [root_cert_fileordir]
        else:
            raise Exception("Couldn't find Root certs in %s" % root_cert_fileordir)


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

        logger = logging.getLogger('cred-verifier')

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

    def verify_from_strings(self, gid_string, cred_strings, target_urn,
                            privileges):
        '''Create Credential and GID objects from the given strings,
        and then verify the GID has the right privileges according 
        to the given credentials on the given target.'''
        if gid_string is None:
            return
        def make_cred(cred_string):
            return cred.Credential(string=cred_string)
        return self.verify(gid.GID(string=gid_string),
                           map(make_cred, cred_strings),
                           target_urn,
                           privileges)
        
    def verify_source(self, source_gid, credential):
        '''Ensure the credential is giving privileges to the caller/client.
        Return True iff the given source (client) GID's URN
        is == the given credential's Caller (Owner) URN'''
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
        '''Ensure the credential is giving privileges on the right subject/target.
        Return True if no target is specified, or the target URN
        matches the credential's Object's (target's) URN, else return False.
        No target is required, for example, to ListResources.'''
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
        ''' Return True iff the given credential gives the privilege
        to perform ALL of the privileges (actions) in the given list.
        In particular, the given list of 'privileges' is really a list
        of names of operations. The privileges in credentials are
        each turned in to Rights objects (see sfa/trust/rights.py).
        And the SFA rights table is used to map from names of privileges
        as specified in credentials, to names of operations.'''
        result = True
        privs = credential.get_privileges()
        for priv in privileges:
            if not privs.can_perform(priv):
                self.logger.debug('Privilege %s not found on credential %s of %s', priv, credential.get_gid_object().get_urn(), credential.get_gid_caller().get_urn())
                result = False
        return result

    def verify(self, gid, credentials, target_urn, privileges):
        '''Verify that the given Source GID supplied at least one credential
        in the given list of credentials that has all the privileges required 
        in the privileges list on the given target.
        IE if any of the supplied credentials has a caller that matches gid 
        and a target that matches target_urn, and has all the privileges in 
        the given list, then return the list of credentials that were ok.
        Throw an Exception if we fail to verify any credential.'''

        # Note that here we treat a list of credentials as being options
        # Alternatively could accumulate privileges for example
        # The semantics of the list of credentials is under specified.

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
                failure = "Cert %s doesn't have sufficient privileges" % cred.get_gid_caller().get_urn()
                continue


            print 
            try:
                if not cred.verify(self.root_cert_files):
                    failure = "Couldn't validate credential for caller %s with target %s with any of %d known root certs" % (cred.get_gid_caller().get_urn(), cred.get_gid_object().get_urn(), len(self.root_cert_files))
                    continue
            except Exception, exc:
                failure = "Couldn't validate credential for caller %s with target %s with any of %d known root certs: %s: %s" % (cred.get_gid_caller().get_urn(), cred.get_gid_object().get_urn(), len(self.root_cert_files), exc.__class__.__name__, exc)
                self.logger.info(failure)
                continue
            # If got here it verified
            result.append(cred)

        
        if result and result != list():
            # At least one credential verified ok and was added to the list
            # return that list
            return result
        else:
            # We did not find any credential with sufficient privileges
            # Raise an exception.
            fault_code = 'Insufficient privileges'
            fault_string = 'No credential was found with appropriate privileges. Tried %s. Last failure: %s' % (tried_creds, failure)
            self.logger.error(fault_string)
            raise xmlrpclib.Fault(fault_code, fault_string)


def create_credential(caller_gid, object_gid, expiration, typename, issuer_keyfile, issuer_certfile, trusted_roots, delegatable=False):
    '''Create and Return a Credential object issued by given key/cert for the given caller
    and object GID objects, given life in seconds, and given type.
    Privileges are determined by type per sfa/trust/rights.py
    Privileges are delegatable if requested.'''
    # FIXME: Validate args: my gids, >0 life,
    # type of cred one I can issue
    # and readable key and cert files
    if caller_gid is None:
        raise ValueError("Missing Caller GID")
    if object_gid is None:
        raise ValueError("Missing Object GID")
    if expiration is None:
        raise ValueError("Missing expiration")
    naive_expiration = naiveUTC(expiration)
    duration = naive_expiration - datetime.datetime.utcnow()
    life_secs = duration.seconds + duration.days * 24 * 3600
    if life_secs < 1:
        raise ValueError("Credential expiration is in the past")
    if trusted_roots is None:
        raise ValueError("Missing list of trusted roots")

    if typename is None or typename.strip() == '':
        raise ValueError("Missing credential type")
    typename = typename.strip().lower()
    if typename not in ("user", "sa", "ma", "authority", "slice", "component"):
        raise ValueError("Unknown credential type %s" % typename)

    if not os.path.isfile(issuer_keyfile):
        raise ValueError("Cant read issuer key file %s" % issuer_keyfile)

    if not os.path.isfile(issuer_certfile):
        raise ValueError("Cant read issuer cert file %s" % issuer_certfile)

    issuer_gid = gid.GID(filename=issuer_certfile)
    
    if not (object_gid.get_urn() == issuer_gid.get_urn() or 
        (issuer_gid.get_type().find('authority') == 0 and
         hrn_authfor_hrn(issuer_gid.get_hrn(), object_gid.get_hrn()))):
        raise ValueError("Issuer not authorized to issue credential: Issuer=%s  Target=%s" % (issuer_gid.get_urn(), object_gid.get_urn()))
    


    ucred = cred.Credential()
    # FIXME: Validate the caller_gid and object_gid
    # are my user and slice
    # Do get_issuer and compare to the issuer cert?
    # Or do gid.is_signed_by_cert(issuer_certfile)?
    ucred.set_gid_caller(caller_gid)
    ucred.set_gid_object(object_gid)
    ucred.set_expiration(expiration)
    # Use sfa/trust/rights.py to figure out what privileges
    # the credential should have.
    # user means refresh, resolve, info
    # per the privilege_table that lets users do
    # remove, update, resolve, list, getcredential,
    # listslices, listnodes, getpolicy
    # Note that it does not allow manipulating slivers

    # And every right is delegatable if any are delegatable (default False)
    privileges = rights.determine_rights(typename, None)
    privileges.delegate_all_privileges(delegatable)
    ucred.set_privileges(privileges)
    ucred.encode()
    ucred.set_issuer_keys(issuer_keyfile, issuer_certfile)
    ucred.sign()
    
    try:
        ucred.verify(trusted_roots)
    except Exception, exc:
        raise Exception("Create Credential failed to verify new credential from trusted roots: %s" % exc)

    return ucred


