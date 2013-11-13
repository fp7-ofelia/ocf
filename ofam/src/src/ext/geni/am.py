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
The GPO Reference Aggregate Manager, showing how to implement
the GENI AM API. This AggregateManager has only fake resources.
Invoked from gcf-am.py
The GENI AM API is defined in the AggregateManager class.
"""

import base64
import datetime
import dateutil.parser
import logging
import os
import xml.dom.minidom as minidom
import xmlrpclib
import zlib

import geni
from SecureXMLRPCServer import SecureXMLRPCServer


# See sfa/trust/rights.py
# These are names of operations
# from the rights.py privilege_table
# Credentials may list privileges that
# map to these operations, giving the caller permission
# to perform the functions
RENEWSLIVERPRIV = 'renewsliver'
CREATESLIVERPRIV = 'createsliver'
DELETESLIVERPRIV = 'deleteslice'
SLIVERSTATUSPRIV = 'getsliceresources'
SHUTDOWNSLIVERPRIV = 'shutdown'

# Publicid format resource namespace. EG Resource URNs
# will be <namespace>:resource:<resourcetype>_<resourceid>
# This is something like the name of your AM
# See gen-certs.CERT_AUTHORITY
RESOURCE_NAMESPACE = 'geni//gpo//gcf'

REFAM_MAXLEASE_DAYS = 365


class AggregateManager(object):
    """The public API for a GENI Aggregate Manager.  This class provides the
    XMLRPC interface and invokes a delegate for all the operations.
    """

    def __init__(self, delegate):
        self._delegate = delegate
        
    def GetVersion(self):
        '''Specify version information about this AM. That could 
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        return self._delegate.GetVersion()

    def ListResources(self, credentials, options):
        '''Return an RSpec of resources managed at this AM. 
        If a geni_slice_urn
        is given in the options, then only return resources assigned 
        to that slice. If geni_available is specified in the options,
        then only report available resources. And if geni_compressed
        option is specified, then compress the result.'''
        return self._delegate.ListResources(credentials, options)

    def CreateSliver(self, slice_urn, credentials, rspec, users):
        """Create a sliver with the given URN from the resources in 
        the given RSpec.
        Return an RSpec of the actually allocated resources.
        users argument provides extra information on configuring the resources
        for runtime access.
        """
        return self._delegate.CreateSliver(slice_urn, credentials, rspec, users)

    def DeleteSliver(self, slice_urn, credentials):
        """Delete the given sliver. Return true on success."""
        return self._delegate.DeleteSliver(slice_urn, credentials)

    def SliverStatus(self, slice_urn, credentials):
        '''Report as much as is known about the status of the resources
        in the sliver. The AM may not know.'''
        return self._delegate.SliverStatus(slice_urn, credentials)

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        """Extend the life of the given sliver until the given
        expiration time. Return False on error."""
        return self._delegate.RenewSliver(slice_urn, credentials,
                                          expiration_time)

    def Shutdown(self, slice_urn, credentials):
        '''For Management Authority / operator use: shut down a badly
        behaving sliver, without deleting it to allow for forensics.'''
        return self._delegate.Shutdown(slice_urn, credentials)

class PrintingAggregateManager(object):
    """A dummy AM that prints the called methods."""

    def GetVersion(self):
        print 'GetVersion()'
        return 1

    def ListResources(self, credentials, options):
        compressed = False
        if options and 'geni_compressed' in options:
            compressed  = options['geni_compressed']
        print 'ListResources(compressed=%r)' % (compressed)
        # return an empty rspec
        result = '<rspec type="GCF"/>'
        if compressed:
            result = xmlrpclib.Binary(zlib.compress(result))
        return result

    def CreateSliver(self, slice_urn, credentials, rspec, users):
        print 'CreateSliver(%r)' % (slice_urn)
        return '<rspec type="GCF"/>'

    def DeleteSliver(self, slice_urn, credentials):
        print 'DeleteSliver(%r)' % (slice_urn)
        return False

    def SliverStatus(self, slice_urn, credentials):
        print 'SliverStatus(%r)' % (slice_urn)
        raise Exception('No such slice.')

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        print 'SliverStatus(%r, %r)' % (slice_urn, expiration_time)
        return False

    def Shutdown(self, slice_urn, credentials):
        print 'Shutdown(%r)' % (slice_urn)
        return False


class AggregateManagerServer(object):
    """An XMLRPC Aggregate Manager Server. Delegates calls to given delegate,
    or the default printing AM."""

    def __init__(self, addr, delegate=None, keyfile=None, certfile=None,
                 ca_certs=None, base_name=None):
        # ca_certs arg here must be a file of concatenated certs
        if ca_certs is None:
            raise Exception('Missing CA Certs')
        elif not os.path.isfile(os.path.expanduser(ca_certs)):
            raise Exception('CA Certs must be an existing file of accepted root certs: %s' % ca_certs)

#        self._server = SecureXMLRPCServer(addr, keyfile=keyfile,
#                                          certfile=certfile, ca_certs=ca_certs)
        from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
        self._server = SecureXMLRPCServer(addr, requestHandler=SimpleXMLRPCRequestHandler)
        if not hasattr(self._server, 'pem_cert'):
            self._server.pem_cert = None
        if delegate is None:
            delegate = PrintingAggregateManager()
        self._server.register_instance(AggregateManager(delegate))
        # Set the server on the delegate so it can access the
        # client certificate.
        delegate._server = self._server
        
        if not base_name is None:
            global RESOURCE_NAMESPACE
            RESOURCE_NAMESPACE = base_name

    def serve_forever(self):
        self._server.serve_forever()

    def register_instance(self, instance):
        # Pass the AM instance to the generic XMLRPC server,
        # which lets it know what XMLRPC methods to expose
        self._server.register_instance(instance)



class Resource(object):
    """A Resource has an id, a type, and a boolean indicating availability."""
    
    STATUS_CONFIGURING = 'configuring'
    STATUS_READY = 'ready'
    STATUS_FAILED = 'failed'
    STATUS_UNKNOWN = 'unknown'
    STATUS_SHUTDOWN = 'shutdown'

    def __init__(self, id, type):
        self._id = id
        self._type = type
        self.available = True
        self.status = Resource.STATUS_UNKNOWN

    def urn(self):
        # User in SliverStatus
        publicid = 'IDN %s//resource//%s_%s' % (RESOURCE_NAMESPACE, self._type, str(self._id))
        return geni.publicid_to_urn(publicid)

    def toxml(self):
        template = ('<resource><urn>%s</urn><type>%s</type><id>%s</id>'
                    + '<available>%r</available></resource>')
        return template % (self.urn(), self._type, self._id, self.available)

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
    """A sliver has a URN, a list of resources, and an expiration time in UTC."""

    def __init__(self, urn, expiration=datetime.datetime.utcnow()):
        self.urn = urn.replace("+slice+", "+sliver+")
        self.resources = list()
        self.expiration = expiration
        
    def status(self):
        """Determine the status of the sliver by examining the status
        of each resource in the sliver.
        """
        # If any resource is 'shutdown', the sliver is 'shutdown'
        # Else if any resource is 'failed', the sliver is 'failed'
        # Else if any resource is 'configuring', the sliver is 'configuring'
        # Else if all resources are 'ready', the sliver is 'ready'
        # Else the sliver is 'unknown'
        rstat = [res.status for res in self.resources]
        if Resource.STATUS_SHUTDOWN in rstat:
            return Resource.STATUS_SHUTDOWN
        elif Resource.STATUS_FAILED in rstat:
            return Resource.STATUS_FAILED
        elif Resource.STATUS_CONFIGURING in rstat:
            return Resource.STATUS_CONFIGURING
        elif rstat == [Resource.STATUS_READY for res in self.resources]:
            # All resources report status of ready
            return Resource.STATUS_READY
        else:
            return Resource.STATUS_UNKNOWN

class ReferenceAggregateManager(object):
    '''A reference Aggregate Manager that manages fake resources.'''
    
    # root_cert is a single cert or dir of multiple certs
    # that are trusted to sign credentials
    def __init__(self, root_cert):
        self._slivers = dict()
        self._resources = [Resource(x, 'Nothing') for x in range(10)]
        self._cred_verifier = geni.CredentialVerifier(root_cert)
        self.max_lease = datetime.timedelta(days=REFAM_MAXLEASE_DAYS)
        self.logger = logging.getLogger('gcf-am.reference')

    def GetVersion(self):
        '''Specify version information about this AM. That could 
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        self.logger.info("Called GetVersion")
        # FIXME: Fill in correct values for others
        # url
        # urn
        # hostname
        # code_tag
        # hrn
        defad = dict(type="GCF", version="0.1")
        # FIXME: Those schema/namespace values are bogus. But the spec also says they are optional.
        reqver = [dict(type="GCF", version="0.1", schema="http://www.geni.net/resources/rspec/0.1/gcf-request.xsd", namespace="http://www.geni.net/resources/rspec/0.1", extensions=[])]
        adver = [dict(type="GCF", version="0.1", schema="http://www.geni.net/resources/rspec/0.1/gcf-ad.xsd", namespace="http://www.geni.net/resources/rspec/0.1", extensions=[])]
        versions = dict(default_ad_rspec=defad, geni_api=1, request_rspec_versions=reqver, ad_rspec_versions=adver, interface='aggregate', url='FIXME', urn='FIXME', hostname='FIXME', code_tag='FIXME', hrn='FIXME')
        return versions

    # The list of credentials are options - some single cred
    # must give the caller required permissions.
    # The semantics of the API are unclear on this point, so 
    # this is just the current implementation
    def ListResources(self, credentials, options):
        '''Return an RSpec of resources managed at this AM. 
        If a geni_slice_urn
        is given in the options, then only return resources assigned 
        to that slice. If geni_available is specified in the options,
        then only report available resources. And if geni_compressed
        option is specified, then compress the result.'''
        self.logger.info('ListResources(%r)' % (options))
        # Note this list of privileges is really the name of an operation
        # from the privilege_table in sfa/trust/rights.py
        # Credentials will specify a list of privileges, each of which
        # confers the right to perform a list of operations.
        # EG the 'info' privilege in a credential allows the operations
        # listslices, listnodes, policy

        # could require list or listnodes?
        privileges = ()
        # Note that verify throws an exception on failure.
        # Use the client PEM format cert as retrieved
        # from the https connection by the SecureXMLRPCServer
        # to identify the caller.
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                None,
                                                privileges)
        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.

        if not options:
            options = dict()

        # Look to see what RSpec version the client requested
        if 'rspec_version' in options:
            # we only have one, so nothing to do here
            # But an AM with multiple formats supported
            # would use this to decide how to format the return.

            # Can also error-check that the input value is supported.
            rspec_type = options['rspec_version']['type']
            rspec_version = options['rspec_version']['version']
            if rspec_type is not 'GCF':
                self.logger.warn("Returning GCF rspec even though request said %s", rspec_type)
            self.logger.info("ListResources requested rspec %s (%d)", rspec_type, rspec_version)

        if 'geni_slice_urn' in options:
            slice_urn = options['geni_slice_urn']
            if slice_urn in self._slivers:
                sliver = self._slivers[slice_urn]
                result = ('<rspec type="GCF">'
                          + ''.join([x.toxml() for x in sliver.resources])
                          + '</rspec>')
            else:
                # return an empty rspec
                result = '<rspec type="GCF"/>'
        elif 'geni_available' in options and options['geni_available']:
            result = ('<rspec type="GCF">' + ''.join([x.toxml() for x in self._resources])
                      + '</rspec>')
            # To make this AM return a fixed RSpec do:
            # rspecfile = open('/tmp/sample-of-ad-rspec.xml')
            # result = ''
            # for line in rspecfile:
            #     result += line
            # rspecfile.close()
        else:
            all_resources = list()
            all_resources.extend(self._resources)
            for sliver in self._slivers:
                all_resources.extend(self._slivers[sliver].resources)
            result = ('<rspec type="GCF">' + ''.join([x.toxml() for x in all_resources])
                      + '</rspec>')

#        self.logger.debug('Returning resource list %s', result)
            # To make this AM return a fixed RSpec do:
            # rspecfile = open('/tmp/sample-of-ad-rspec.xml')
            # result = ''
            # for line in rspecfile:
            #     result += line
            # rspecfile.close()

        # Optionally compress the result
        if 'geni_compressed' in options and options['geni_compressed']:
            try:
                result = base64.b64encode(zlib.compress(result))
            except Exception, exc:
                import traceback
                self.logger.error("Error compressing and encoding resource list: %s", traceback.format_exc())
                raise Exception("Server error compressing resource list", exc)

        return result

    # The list of credentials are options - some single cred
    # must give the caller required permissions.
    # The semantics of the API are unclear on this point, so 
    # this is just the current implementation
    def CreateSliver(self, slice_urn, credentials, rspec, users):
        """Create a sliver with the given URN from the resources in 
        the given RSpec.
        Return an RSpec of the actually allocated resources.
        users argument provides extra information on configuring the resources
        for runtime access.
        """
        self.logger.info('CreateSliver(%r)' % (slice_urn))
        # Note this list of privileges is really the name of an operation
        # from the privilege_table in sfa/trust/rights.py
        # Credentials will specify a list of privileges, each of which
        # confers the right to perform a list of operations.
        # EG the 'info' privilege in a credential allows the operations
        # listslices, listnodes, policy
        privileges = (CREATESLIVERPRIV,)
        # Note that verify throws an exception on failure.
        # Use the client PEM format cert as retrieved
        # from the https connection by the SecureXMLRPCServer
        # to identify the caller.
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.
        if slice_urn in self._slivers:
            self.logger.error('Sliver %s already exists.' % slice_urn)
            raise Exception('Sliver %s already exists.' % slice_urn)

        rspec_dom = None
        try:
            rspec_dom = minidom.parseString(rspec)
        except Exception, exc:
            self.logger.error("Cant create sliver %s. Exception parsing rspec: %s" % (slice_urn, exc))
            raise Exception("Cant create sliver %s. Exception parsing rspec: %s" % (slice_urn, exc))


        # Look at the version of the input request RSpec
        # Make sure it is supported
        # Then make sure that you return an RSpec in the same format
        # EG if both V1 and V2 are supported, and the user gives V2 request,
        # then you must return a V2 request and not V1

        resources = list()
        for elem in rspec_dom.documentElement.getElementsByTagName('resource'):
            resource = None
            try:
                resource = Resource.fromdom(elem)
            except Exception, exc:
                import traceback
                self.logger.warning("Failed to parse resource from RSpec dom: %s", traceback.format_exc())
                raise Exception("Cant create sliver %s. Exception parsing rspec: %s" % (slice_urn, exc))

            if resource not in self._resources:
                self.logger.info("Requested resource %d not available" % resource._id)
                raise Exception('Resource %d not available' % resource._id)
            resources.append(resource)

        # determine max expiration time from credentials
        # do not create a sliver that will outlive the slice!
        expiration = datetime.datetime.utcnow() + self.max_lease
        for cred in creds:
            credexp = self._naiveUTC(cred.expiration)
            if credexp < expiration:
                expiration = credexp

        sliver = Sliver(slice_urn, expiration)

        # remove resources from available list
        for resource in resources:
            sliver.resources.append(resource)
            self._resources.remove(resource)
            resource.available = False
            resource.status = Resource.STATUS_READY

        self._slivers[slice_urn] = sliver

        self.logger.info("Created new sliver for slice %s" % slice_urn)
        return ('<rspec type="GCF">' + ''.join([x.toxml() for x in sliver.resources])
                + '</rspec>')

    # The list of credentials are options - some single cred
    # must give the caller required permissions.
    # The semantics of the API are unclear on this point, so 
    # this is just the current implementation
    def DeleteSliver(self, slice_urn, credentials):
        '''Stop and completely delete the named sliver, and return True.'''
        self.logger.info('DeleteSliver(%r)' % (slice_urn))
        # Note this list of privileges is really the name of an operation
        # from the privilege_table in sfa/trust/rights.py
        # Credentials will specify a list of privileges, each of which
        # confers the right to perform a list of operations.
        # EG the 'info' privilege in a credential allows the operations
        # listslices, listnodes, policy
        privileges = (DELETESLIVERPRIV,)
        # Note that verify throws an exception on failure.
        # Use the client PEM format cert as retrieved
        # from the https connection by the SecureXMLRPCServer
        # to identify the caller.
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            if sliver.status() == Resource.STATUS_SHUTDOWN:
                self.logger.info("Sliver %s not deleted because it is shutdown",
                                 slice_urn)
                return False
            # return the resources to the pool
            self._resources.extend(sliver.resources)
            for resource in sliver.resources:
                resource.available = True
                resource.status = Resource.STATUS_UNKNOWN
            del self._slivers[slice_urn]
            self.logger.info("Sliver %r deleted" % slice_urn)
            return True
        else:
            self.no_such_slice(slice_urn)

    def SliverStatus(self, slice_urn, credentials):
        '''Report as much as is known about the status of the resources
        in the sliver. The AM may not know.
        Return a dict of sliver urn, status, and a list of dicts resource
        statuses.'''
        # Loop over the resources in a sliver gathering status.
        self.logger.info('SliverStatus(%r)' % (slice_urn))
        # Note this list of privileges is really the name of an operation
        # from the privilege_table in sfa/trust/rights.py
        # Credentials will specify a list of privileges, each of which
        # confers the right to perform a list of operations.
        # EG the 'info' privilege in a credential allows the operations
        # listslices, listnodes, policy
        privileges = (SLIVERSTATUSPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            # Now calculate the status of the sliver
            res_status = list()
            for res in sliver.resources:
                # Gather the status of all the resources
                # in the sliver. This could be actually
                # communicating with the resources, or simply
                # reporting the state of initialized, started, stopped, ...
                res_status.append(dict(geni_urn=res.urn(),
                                       geni_status=res.status,
                                       geni_error=''))
            self.logger.info("Calculated and returning sliver %r status" % slice_urn)
            return dict(geni_urn=sliver.urn,
                        geni_status=sliver.status(),
                        geni_resources=res_status)
        else:
            self.no_such_slice(slice_urn)

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        '''Renew the local sliver that is part of the named Slice
        until the given expiration time (in UTC with a TZ per RFC3339).
        Requires at least one credential that is valid until then.
        Return False on any error, True on success.'''

        self.logger.info('RenewSliver(%r, %r)' % (slice_urn, expiration_time))
        privileges = (RENEWSLIVERPRIV,)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        # All the credentials we just got are valid
        if slice_urn in self._slivers:
            # If any credential will still be valid at the newly 
            # requested time, then we can do this.
            sliver = self._slivers.get(slice_urn)
            if sliver.status() == Resource.STATUS_SHUTDOWN:
                self.logger.info("Sliver %s not renewed because it is shutdown",
                                 slice_urn)
                return False
            requested = dateutil.parser.parse(str(expiration_time))
            # Per the AM API, the input time should be TZ-aware
            # But since the slice cred may not (per ISO8601), convert
            # it to naiveUTC for comparison
            requested = self._naiveUTC(requested)
            lastexp = 0
            for cred in creds:
                credexp = self._naiveUTC(cred.expiration)
                lastexp = credexp
                if credexp >= requested:
                    sliver.expiration = requested
                    self.logger.info("Sliver %r now expires on %r", slice_urn, expiration_time)
                    return True
                else:
                    self.logger.debug("Valid cred %r expires at %r before %r", cred, credexp, requested)

            # Fell through then no credential expires at or after
            # newly requested expiration time
            self.logger.info("Can't renew sliver %r until %r because none of %d credential(s) valid until then (last expires at %r)", slice_urn, expiration_time, len(creds), str(lastexp))
            # FIXME: raise an exception so the client knows what
            # really went wrong?
            return False

        else:
            self.no_such_slice(slice_urn)

    def Shutdown(self, slice_urn, credentials):
        '''For Management Authority / operator use: shut down a badly
        behaving sliver, without deleting it to allow for forensics.'''
        self.logger.info('Shutdown(%r)' % (slice_urn))
        privileges = (SHUTDOWNSLIVERPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        if slice_urn in self._slivers:
            sliver = self._slivers[slice_urn]
            for resource in sliver.resources:
                resource.status = Resource.STATUS_SHUTDOWN
            self.logger.info("Sliver %r shut down" % slice_urn)
            return True
        else:
            self.logger.info("Shutdown: No such slice: %s.", slice_urn)
            self.no_such_slice(slice_urn)

    def no_such_slice(self, slice_urn):
        """Raise a no such slice exception."""
        fault_code = 'No such slice.'
        fault_string = 'The slice named by %s does not exist' % (slice_urn)
        self.logger.warning(fault_string)
        raise xmlrpclib.Fault(fault_code, fault_string)

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

