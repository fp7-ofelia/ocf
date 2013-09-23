#----------------------------------------------------------------------
# Copyright (c) 2011-2013 Raytheon BBN Technologies
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
The GPO Reference Aggregate Manager v2, showing how to implement
the GENI AM API version 2. This AggregateManager has only fake resources.
Invoked from gcf-am.py
The GENI AM API is defined in the AggregateManager class.
"""

import base64
import datetime
import dateutil.parser
import logging
import os
import uuid
import xml.dom.minidom as minidom
import xmlrpclib
import zlib

import geni
from geni.util.urn_util import publicid_to_urn
from geni.SecureXMLRPCServer import SecureXMLRPCServer
from resource import Resource
from aggregate import Aggregate
from fakevm import FakeVM


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


class Slice(object):
    """A slice has a URN, a list of resources, and an expiration time in UTC."""

    def __init__(self, urn, expiration):
        self.id = str(uuid.uuid4())
        self.urn = urn
        self.expiration = expiration
        self.resources = dict()

    def status(self, resources):
        """Determine the status of the sliver by examining the status
        of each resource in the sliver.
        """
        # If any resource is 'shutdown', the sliver is 'shutdown'
        # Else if any resource is 'failed', the sliver is 'failed'
        # Else if any resource is 'configuring', the sliver is 'configuring'
        # Else if all resources are 'ready', the sliver is 'ready'
        # Else the sliver is 'unknown'
        rstat = [res.status for res in resources]
        if Resource.STATUS_SHUTDOWN in rstat:
            return Resource.STATUS_SHUTDOWN
        elif Resource.STATUS_FAILED in rstat:
            return Resource.STATUS_FAILED
        elif Resource.STATUS_CONFIGURING in rstat:
            return Resource.STATUS_CONFIGURING
        elif rstat == [Resource.STATUS_READY for res in self.resources.values()]:
            # All resources report status of ready
            return Resource.STATUS_READY
        else:
            return Resource.STATUS_UNKNOWN


class ReferenceAggregateManager(object):
    '''A reference Aggregate Manager that manages fake resources.'''

    # root_cert is a single cert or dir of multiple certs
    # that are trusted to sign credentials
    def __init__(self, root_cert, urn_authority, url):
        self._url = url
        self._api_version = 2
        self._slices = dict()
        self._agg = Aggregate()
        self._agg.add_resources([FakeVM(self._agg) for _ in range(3)])
        self._cred_verifier = geni.CredentialVerifier(root_cert)
        self._urn_authority = urn_authority
        self._my_urn = publicid_to_urn("%s %s %s" % (self._urn_authority, 'authority', 'am'))
        self.max_lease = datetime.timedelta(days=REFAM_MAXLEASE_DAYS)
        self.logger = logging.getLogger('gcf.am2')

    def GetVersion(self, options):
        '''Specify version information about this AM. That could
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        self.logger.info("Called GetVersion")
        reqver = [dict(type="geni",
                       version="3",
                       schema="http://www.geni.net/resources/rspec/3/request.xsd",
                       namespace="http://www.geni.net/resources/rspec/3",
                       extensions=[])]
        adver = [dict(type="geni",
                      version="3",
                      schema="http://www.geni.net/resources/rspec/3/ad.xsd",
                      namespace="http://www.geni.net/resources/rspec/3",
                      extensions=[])]
        api_versions = dict()
        api_versions[str(self._api_version)] = self._url
        versions = dict(geni_api=2,
                        geni_api_versions=api_versions,
                        geni_request_rspec_versions=reqver,
                        geni_ad_rspec_versions=adver)
        return dict(geni_api=versions['geni_api'],
                    code=dict(geni_code=0,
                              am_type="gcf2",
                              am_code=0),
                    value=versions,
                    output="")

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
        try:
            self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                    credentials,
                                                    None,
                                                    privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.

        if 'geni_rspec_version' not in options:
            # This is a required option, so error out with bad arguments.
            self.logger.error('No geni_rspec_version supplied to ListResources.')
            return self.errorResult(1, 'Bad Arguments: option geni_rspec_version was not supplied.')
        if 'type' not in options['geni_rspec_version']:
            self.logger.error('ListResources: geni_rspec_version does not contain a type field.')
            return self.errorResult(1, 'Bad Arguments: option geni_rspec_version does not have a type field.')
        if 'version' not in options['geni_rspec_version']:
            self.logger.error('ListResources: geni_rspec_version does not contain a version field.')
            return self.errorResult(1, 'Bad Arguments: option geni_rspec_version does not have a version field.')

        # Look to see what RSpec version the client requested
        # Error-check that the input value is supported.
        rspec_type = options['geni_rspec_version']['type']
        if isinstance(rspec_type, str):
            rspec_type = rspec_type.lower().strip()
        rspec_version = options['geni_rspec_version']['version']
        if rspec_type != 'geni':
            self.logger.error('ListResources: Unknown RSpec type %s requested', rspec_type)
            return self.errorResult(4, 'Bad Version: requested RSpec type %s is not a valid option.' % (rspec_type))
        if rspec_version != '3':
            self.logger.error('ListResources: Unknown RSpec version %s requested', rspec_version)
            return self.errorResult(4, 'Bad Version: requested RSpec version %s is not a valid option.' % (rspec_type))
        self.logger.info("ListResources requested RSpec %s (%s)", rspec_type, rspec_version)

        if 'geni_slice_urn' in options:
            slice_urn = options['geni_slice_urn']
            if slice_urn in self._slices:
                result = self.manifest_rspec(slice_urn)
            else:
                # return an empty rspec
                return self._no_such_slice(slice_urn)
        else:
            all_resources = self._agg.catalog(None)
            available = 'geni_available' in options and options['geni_available']
            resource_xml = ""
            for r in all_resources:
                if available and not r.available:
                    continue
                resource_xml = resource_xml + self.advert_resource(r)
            result = self.advert_header() + resource_xml + self.advert_footer()
        self.logger.debug("Result is now \"%s\"", result)
        # Optionally compress the result
        if 'geni_compressed' in options and options['geni_compressed']:
            try:
                result = base64.b64encode(zlib.compress(result))
            except Exception, exc:
                import traceback
                self.logger.error("Error compressing and encoding resource list: %s", traceback.format_exc())
                raise Exception("Server error compressing resource list", exc)

        return dict(code=dict(geni_code=0,
                              am_type="gcf2",
                              am_code=0),
                    value=result,
                    output="")

    # The list of credentials are options - some single cred
    # must give the caller required permissions.
    # The semantics of the API are unclear on this point, so
    # this is just the current implementation
    def CreateSliver(self, slice_urn, credentials, rspec, users, options):
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
        try:
            creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                            credentials,
                                                            slice_urn,
                                                            privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.
        if slice_urn in self._slices:
            self.logger.error('Slice %s already exists.', slice_urn)
            return self.errorResult(17, 'Slice %s already exists' % (slice_urn))

        rspec_dom = None
        try:
            rspec_dom = minidom.parseString(rspec)
        except Exception, exc:
            self.logger.error("Cant create sliver %s. Exception parsing rspec: %s" % (slice_urn, exc))
            return self.errorResult(1, 'Bad Args: RSpec is unparseable')

        # Look at the version of the input request RSpec
        # Make sure it is supported
        # Then make sure that you return an RSpec in the same format
        # EG if both V1 and V2 are supported, and the user gives V2 request,
        # then you must return a V2 request and not V1

        allresources = self._agg.catalog()
        allrdict = dict()
        for r in allresources:
            if r.available:
                allrdict[r.id] = r

        # Note: This only handles unbound nodes. Any attempt by the client
        # to specify a node is ignored.
        resources = dict()
        unbound = list()
        for elem in rspec_dom.documentElement.getElementsByTagName('node'):
            unbound.append(elem)
        for elem in unbound:
            client_id = elem.getAttribute('client_id')
            keys = allrdict.keys()
            if keys:
                rid = keys[0]
                resources[client_id] = allrdict[rid]
                del allrdict[rid]
            else:
                return self.errorResult(6, 'Too Big: insufficient resources to fulfill request')

        # determine max expiration time from credentials
        # do not create a sliver that will outlive the slice!
        expiration = datetime.datetime.utcnow() + self.max_lease
        for cred in creds:
            credexp = self._naiveUTC(cred.expiration)
            if credexp < expiration:
                expiration = credexp

        newslice = Slice(slice_urn, expiration)
        self._agg.allocate(slice_urn, resources.values())
        for cid, r in resources.items():
            newslice.resources[cid] = r.id
            r.status = Resource.STATUS_READY
        self._slices[slice_urn] = newslice

        self.logger.info("Created new slice %s" % slice_urn)
        result = self.manifest_rspec(slice_urn)
        self.logger.debug('Result = %s', result)
        return dict(code=dict(geni_code=0,
                              am_type="gcf2",
                              am_code=0),
                    value=result,
                    output="")

    # The list of credentials are options - some single cred
    # must give the caller required permissions.
    # The semantics of the API are unclear on this point, so
    # this is just the current implementation
    def DeleteSliver(self, slice_urn, credentials, options):
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
        try:
            self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                    credentials,
                                                    slice_urn,
                                                    privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        # If we get here, the credentials give the caller
        # all needed privileges to act on the given target.
        if slice_urn in self._slices:
            sliver = self._slices[slice_urn]
            resources = self._agg.catalog(slice_urn)
            if sliver.status(resources) == Resource.STATUS_SHUTDOWN:
                self.logger.info("Sliver %s not deleted because it is shutdown",
                                 slice_urn)
                return self.errorResult(11, "Unavailable: Slice %s is unavailable." % (slice_urn))
            self._agg.deallocate(slice_urn, None)
            for r in resources:
                r.status = Resource.STATUS_UNKNOWN
            del self._slices[slice_urn]
            self.logger.info("Sliver %r deleted" % slice_urn)
            return self.successResult(True)
        else:
            return self._no_such_slice(slice_urn)


    def SliverStatus(self, slice_urn, credentials, options):
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
        try:
            self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                    credentials,
                                                    slice_urn,
                                                    privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        if slice_urn in self._slices:
            theSlice = self._slices[slice_urn]
            # Now calculate the status of the sliver
            res_status = list()
            resources = self._agg.catalog(slice_urn)
            for res in resources:
                self.logger.debug('Resource = %s', str(res))
                # Gather the status of all the resources
                # in the sliver. This could be actually
                # communicating with the resources, or simply
                # reporting the state of initialized, started, stopped, ...
                res_status.append(dict(geni_urn=self.resource_urn(res),
                                       geni_status=res.status,
                                       geni_error=''))
            self.logger.info("Calculated and returning slice %s status", slice_urn)
            result = dict(geni_urn=slice_urn,
                          geni_status=theSlice.status(resources),
                          geni_resources=res_status)
            return dict(code=dict(geni_code=0,
                                  am_type="gcf2",
                                  am_code=0),
                        value=result,
                        output="")
        else:
            return self._no_such_slice(slice_urn)

    def RenewSliver(self, slice_urn, credentials, expiration_time, options):
        '''Renew the local sliver that is part of the named Slice
        until the given expiration time (in UTC with a TZ per RFC3339).
        Requires at least one credential that is valid until then.
        Return False on any error, True on success.'''

        self.logger.info('RenewSliver(%r, %r)' % (slice_urn, expiration_time))
        privileges = (RENEWSLIVERPRIV,)
        try:
            creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                            credentials,
                                                            slice_urn,
                                                            privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        # All the credentials we just got are valid
        if slice_urn in self._slices:
            # If any credential will still be valid at the newly
            # requested time, then we can do this.
            resources = self._agg.catalog(slice_urn)
            sliver = self._slices.get(slice_urn)
            if sliver.status(resources) == Resource.STATUS_SHUTDOWN:
                self.logger.info("Sliver %s not renewed because it is shutdown",
                                 slice_urn)
                return self.errorResult(11, "Unavailable: Slice %s is unavailable." % (slice_urn))
            requested = dateutil.parser.parse(str(expiration_time))
            # Per the AM API, the input time should be TZ-aware
            # But since the slice cred may not (per ISO8601), convert
            # it to naiveUTC for comparison
            requested = self._naiveUTC(requested)
            maxexp = datetime.datetime.min
            for cred in creds:
                credexp = self._naiveUTC(cred.expiration)
                if credexp > maxexp:
                    maxexp = credexp
                maxexp = credexp
                if credexp >= requested:
                    sliver.expiration = requested
                    self.logger.info("Sliver %r now expires on %r", slice_urn, expiration_time)
                    return self.successResult(True)
                else:
                    self.logger.debug("Valid cred %r expires at %r before %r", cred, credexp, requested)

            # Fell through then no credential expires at or after
            # newly requested expiration time
            self.logger.info("Can't renew sliver %r until %r because none of %d credential(s) valid until then (latest expires at %r)", slice_urn, expiration_time, len(creds), maxexp)
            # FIXME: raise an exception so the client knows what
            # really went wrong?
            return self.errorResult(19, "Out of range: Expiration %s is out of range (past last credential expiration of %s)." % (expiration_time, maxexp))

        else:
            return self._no_such_slice(slice_urn)

    def Shutdown(self, slice_urn, credentials, options):
        '''For Management Authority / operator use: shut down a badly
        behaving sliver, without deleting it to allow for forensics.'''
        self.logger.info('Shutdown(%r)' % (slice_urn))
        privileges = (SHUTDOWNSLIVERPRIV,)
        try:
            self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                    credentials,
                                                    slice_urn,
                                                    privileges)
        except Exception, e:
            raise xmlrpclib.Fault('Insufficient privileges', str(e))

        if slice_urn in self._slices:
            resources = self._agg.catalog(slice_urn)
            for resource in resources:
                resource.status = Resource.STATUS_SHUTDOWN
            self.logger.info("Sliver %r shut down" % slice_urn)
            return self.successResult(True)
        else:
            self.logger.info("Shutdown: No such slice: %s.", slice_urn)
            return self._no_such_slice(slice_urn)

    def successResult(self, value):
        code_dict = dict(geni_code=0,
                         am_type="gcf2",
                         am_code=0)
        return dict(code=code_dict,
                    value=value,
                    output="")

    def _no_such_slice(self, slice_urn):
        return self.errorResult(12, 'Search Failed: no slice "%s" found' % (slice_urn))

    def errorResult(self, code, output, am_code=None):
        code_dict = dict(geni_code=code, am_type="gcf2")
        if am_code is not None:
            code_dict['am_code'] = am_code
        return dict(code=code_dict,
                    value="",
                    output=output)

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

    def advert_resource(self, resource):
        tmpl = '''  <node component_manager_id="%s"
        component_name="%s"
        component_id="%s"
        exclusive="%s">
    <available now="%s"/>
  </node>
  '''
        resource_id = str(resource.id)
        resource_exclusive = str(False).lower()
        resource_available = str(resource.available).lower()
        resource_urn = self.resource_urn(resource)
        return tmpl % (self._my_urn,
                       resource_id,
                       resource_urn,
                       resource_exclusive,
                       resource_available)

    def advert_header(self):
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd"
       type="advertisement">'''
        return header

    def advert_footer(self):
        return '</rspec>'

    def manifest_header(self):
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd"
       type="manifest">'''
        return header

    def manifest_slice(self, slice_urn):
        tmpl = '<node client_id="%s"/>'
        result = ""
        for cid in self._slices[slice_urn].resources.keys():
            result = result + tmpl % (cid)
        return result

    def manifest_footer(self):
        return '</rspec>'

    def manifest_rspec(self, slice_urn):
        return self.manifest_header() + self.manifest_slice(slice_urn) + self.manifest_footer()

    def resource_urn(self, resource):
        urn = publicid_to_urn("%s %s %s" % (self._urn_authority,
                                            str(resource.type),
                                            str(resource.id)))
        return urn


class AggregateManager(object):
    """The public API for a GENI Aggregate Manager.  This class provides the
    XMLRPC interface and invokes a delegate for all the operations.
    """

    def __init__(self, delegate):
        self._delegate = delegate
        self.logger = logging.getLogger('gcf.am2')

    def _exception_result(self, exception):
        output = str(exception)
        self.logger.warning(output)
        # XXX Code for no slice here?
        return dict(code=dict(geni_code=102,
                              am_type="gcf2",
                              am_code=0),
                    value="",
                    output=output)

    def GetVersion(self, options=dict()):
        '''Specify version information about this AM. That could
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        try:
            return self._delegate.GetVersion(options)
        except Exception as e:
            self.logger.exception("Error in GetVersion:")
            return self._exception_result(e)

    def ListResources(self, credentials, options):
        '''Return an RSpec of resources managed at this AM.
        If a geni_slice_urn
        is given in the options, then only return resources assigned
        to that slice. If geni_available is specified in the options,
        then only report available resources. And if geni_compressed
        option is specified, then compress the result.'''
        try:
            return self._delegate.ListResources(credentials, options)
        except Exception as e:
            self.logger.exception("Error in ListResources:")
            return self._exception_result(e)

    def CreateSliver(self, slice_urn, credentials, rspec, users, options):
        """Create a sliver with the given URN from the resources in
        the given RSpec.
        Return an RSpec of the actually allocated resources.
        users argument provides extra information on configuring the resources
        for runtime access.
        """
        try:
            return self._delegate.CreateSliver(slice_urn, credentials, rspec,
                                               users, options)
        except Exception as e:
            self.logger.exception("Error in CreateSliver:")
            return self._exception_result(e)

    def DeleteSliver(self, slice_urn, credentials, options):
        """Delete the given sliver. Return true on success."""
        try:
            return self._delegate.DeleteSliver(slice_urn, credentials, options)
        except Exception as e:
            self.logger.exception("Error in DeleteSliver:")
            return self._exception_result(e)

    def SliverStatus(self, slice_urn, credentials, options):
        '''Report as much as is known about the status of the resources
        in the sliver. The AM may not know.'''
        try:
            return self._delegate.SliverStatus(slice_urn, credentials, options)
        except Exception as e:
            self.logger.exception("Error in SliverStatus:")
            return self._exception_result(e)

    def RenewSliver(self, slice_urn, credentials, expiration_time, options):
        """Extend the life of the given sliver until the given
        expiration time. Return False on error."""
        try:
            return self._delegate.RenewSliver(slice_urn, credentials,
                                              expiration_time, options)
        except Exception as e:
            self.logger.exception("Error in RenewSliver:")
            return self._exception_result(e)

    def Shutdown(self, slice_urn, credentials, options):
        '''For Management Authority / operator use: shut down a badly
        behaving sliver, without deleting it to allow for forensics.'''
        try:
            return self._delegate.Shutdown(slice_urn, credentials, options)
        except Exception as e:
            self.logger.exception("Error in Shutdown:")
            return self._exception_result(e)


class AggregateManagerServer(object):
    """An XMLRPC Aggregate Manager Server. Delegates calls to given delegate,
    or the default printing AM."""

    def __init__(self, addr, keyfile=None, certfile=None,
                 trust_roots_dir=None,
                 ca_certs=None, base_name=None):
        # ca_certs arg here must be a file of concatenated certs
        if ca_certs is None:
            raise Exception('Missing CA Certs')
        elif not os.path.isfile(os.path.expanduser(ca_certs)):
            raise Exception('CA Certs must be an existing file of accepted root certs: %s' % ca_certs)

        # Decode the addr into a URL. Is there a pythonic way to do this?
        server_url = "https://%s:%d/" % addr
        delegate = ReferenceAggregateManager(trust_roots_dir, base_name, 
                                             server_url)
        # FIXME: set logRequests=true if --debug
        self._server = SecureXMLRPCServer(addr, keyfile=keyfile,
                                          certfile=certfile, ca_certs=ca_certs)
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
