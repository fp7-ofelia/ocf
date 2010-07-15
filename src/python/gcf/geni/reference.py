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
from gcf.geni.ch import publicid_to_urn
"""
The GPO Reference Aggregate Manager, showing how to implement
the GENI AM API. This AggregateManager has only fake resources.
Note in particular the CredentialVerifier class that uses
SFA code to verify credentials.
"""

import base64
import datetime
import logging
import os
import xml.dom.minidom as minidom
import xmlrpclib
import zlib
import sys

import dateutil.parser

import gcf.sfa.trust.credential as cred
import gcf.sfa.trust.gid as gid

# See sfa/trust/rights.py
RENEWSLIVERPRIV = 'renewsliver'
RESOURCEPUBLICIDPREFIX = 'geni.net'
CREATESLIVERPRIV = 'createsliver'
DELETESLIVERPRIV = 'deleteslice'
SLIVERSTATUSPRIV = 'getsliceresources'

REFAM_MAXLEASE_DAYS = 365


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

class Resource(object):
    """A Resource has an id, a type, and a boolean indicating availability."""

    def __init__(self, id, type):
        self._id = id
        self._type = type
        self.available = True

    def toxml(self):
        template = ('<resource><type>%s</type><id>%s</id>'
                    + '<available>%r</available></resource>')
        return template % (self._type, self._id, self.available)

    def urn(self):
        publicid = 'IDN %s//resource//%s_%s' % (RESOURCEPUBLICIDPREFIX, self._type, str(self._id))
        return publicid_to_urn(publicid)

    def __eq__(self, other):
        return self._id == other._id

    def __neq__(self, other):
        return self._id != other._id

    @classmethod
    def fromdom(cls, element):
        """Create a Resource instance from a DOM representation."""
        type = element.getElementsByTagName('type')[0].firstChild.data
        id = int(element.getElementsByTagName('id')[0].firstChild.data)
        return Resource(id, type)

class Sliver(object):
    """A sliver has a URN, a list of resoruces, and an expiration time."""

    def __init__(self, urn, expiration=datetime.datetime.now()):
        self.urn = urn
        self.resources = list()
        self.expiration = expiration

class ReferenceAggregateManager(object):
    
    # root_cert is a single cert or dir of multiple certs
    def __init__(self, root_cert):
        self._slivers = dict()
        self._resources = [Resource(x, 'Nothing') for x in range(10)]
        self._cred_verifier = CredentialVerifier(root_cert)
        self.max_lease = datetime.timedelta(days=REFAM_MAXLEASE_DAYS)
        self.logger = logging.getLogger('gam.reference')

    def GetVersion(self):
        self.logger.info("Called GetVersion")
        return dict(geni_api=1)

    def ListResources(self, credentials, options):
        self.logger.info('ListResources(%r)' % (options))
        privileges = ()
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                None,
                                                privileges)

        if not options:
            options = dict()

        if 'geni_slice_urn' in options:
            slice_urn = options['geni_slice_urn']
            if slice_urn in self._slivers:
                sliver = self._slivers[slice_urn]
                result = ('<rspec>'
                          + ''.join([x.toxml() for x in sliver.resources])
                          + '</rspec>')
            else:
                # return an empty rspec
                result = '<rspec/>'
        elif 'geni_available' in options and options['geni_available']:
            result = ('<rspec>' + ''.join([x.toxml() for x in self._resources])
                      + '</rspec>')
        else:
            all_resources = list()
            all_resources.extend(self._resources)
            for sliver in self._slivers:
                all_resources.extend(self._slivers[sliver].resources)
            result = ('<rspec>' + ''.join([x.toxml() for x in all_resources])
                      + '</rspec>')

#        self.logger.debug('Returning resource list %s', result)

        # Optionally compress the result
        if 'geni_compressed' in options and options['geni_compressed']:
            result = base64.b64encode(zlib.compress(result))
        return result

    def CreateSliver(self, slice_urn, credentials, rspec, users):
        self.logger.info('CreateSliver(%r)' % (slice_urn))
        privileges = (CREATESLIVERPRIV,)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        if slice_urn in self._slivers:
            raise Exception('Sliver %s already exists.' % slice_urn)

        rspec_dom = minidom.parseString(rspec)
        resources = list()
        for elem in rspec_dom.documentElement.childNodes:
            resource = Resource.fromdom(elem)
            if resource not in self._resources:
                raise Exception('Resource %d not available' % resource._id)
            resources.append(resource)

        # determine max expiration time from credentials
        expiration = datetime.datetime.now() + self.max_lease
        for cred in creds:
            if cred.expiration < expiration:
                expiration = cred.expiration

        sliver = Sliver(slice_urn, expiration)

        # remove resources from available list
        for resource in resources:
            sliver.resources.append(resource)
            self._resources.remove(resource)
            resource.available = False

        self._slivers[slice_urn] = sliver

        self.logger.info("Created new sliver for slice %s" % slice_urn)
        return ('<rspec>' + ''.join([x.toxml() for x in sliver.resources])
                + '</rspec>')

    def DeleteSliver(self, slice_urn, credentials):
        self.logger.info('DeleteSliver(%r)' % (slice_urn))
        privileges = (DELETESLIVERPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            # return the resources to the pool
            self._resources.extend(sliver.resources)
            for resource in sliver.resources:
                resource.available = True
            del self._slivers[slice_urn]
            self.logger.info("Sliver %r deleted" % slice_urn)
            return True
        else:
            self.no_such_slice(slice_urn)

    def SliverStatus(self, slice_urn, credentials):
        # Loop over the resources in a sliver gathering status.
        self.logger.info('SliverStatus(%r)' % (slice_urn))
        privileges = (SLIVERSTATUSPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            res_status = list()
            for res in sliver.resources:
                res_status.append(dict(geni_urn=res.urn(),
                                       geni_status='ready',
                                       geni_error=''))
            self.logger.info("Calculated and returning sliver %r status" % slice_urn)
            return dict(geni_urn=sliver.urn,
                        # TODO: need to calculate sliver status
                        geni_status='ready',
                        geni_resources=res_status)
        else:
            self.no_such_slice(slice_urn)

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        self.logger.info('RenewSliver(%r, %r)' % (slice_urn, expiration_time))
        privileges = (RENEWSLIVERPRIV,)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        if slice_urn in self._slivers:
            sliver = self._slivers.get(slice_urn)
            requested = dateutil.parser.parse(str(expiration_time))
            for cred in creds:
                # FIXME Should this fail if 1 cred will have expired? Or only if all will be expired?
                # Or in practics is this always a list of 1?
                if cred.expiration < requested:
                    self.logger.debug("Cant renew sliver %r until %r cause one of %d credential(s) (%r) expires before then", slice_urn, expiration_time, len(creds), cred.get_gid_object().get_hrn())
                    return False

            sliver.expiration = requested
            self.logger.info("Sliver %r now expires on %r", slice_urn, expiration_time)
            return True
        else:
            self.no_such_slice(slice_urn)

    def Shutdown(self, slice_urn, credentials):
        self.logger.info('Shutdown(%r)' % (slice_urn))
        # TODO: No permission for Shutdown currently exists.
        privileges = ()
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        if slice_urn in self._slivers:
            return False
        else:
            self.no_such_slice(slice_urn)

    def no_such_slice(self, slice_urn):
        """Raise a no such slice exception."""
        fault_code = 'No such slice.'
        fault_string = 'The slice named by %s does not exist' % (slice_urn)
        raise xmlrpclib.Fault(fault_code, fault_string)
