from django.http import *
import os, sys, logging
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.communication.sfa.authManager import AuthManager
from vt_manager.communication.sfa.util.xrn import urn_to_hrn
from vt_manager.communication.sfa.util.faults import SfaInvalidArgument

from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.callids import Callids

from vt_manager.communication.sfa.VTSfaDriver import VTSfaDriver


# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'
API_TYPE = 'struct'
driver = VTSfaDriver(None)

@rpcmethod(signature=['string', 'string'], url_name="sfa")
def ping(challenge):
    return challenge


@rpcmethod(signature=[VERSION_TYPE, API_TYPE], url_name="sfa")
def GetVersion(api):
    xrn=Xrn(api.hrn)
    version = version_core()
    version_generic = {
        'interface':'aggregate',
        'sfa': 2,
        'geni_api': 2,
        'geni_api_versions': {'2': 'http://%s:%s' % (api.config.SFA_AGGREGATE_HOST, api.config.SFA_AGGREGATE_PORT)},
        'hrn':xrn.get_hrn(),
        'urn':xrn.get_urn(),
    }
    version.update(version_generic)
    testbed_version = driver.aggregate_version()
    version.update(testbed_version)
    return version


@rpcmethod(signature=[RSPEC_TYPE, API_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListResources(api, credentials, options, **kwargs):
    # get slice's hrn from options    
    slice_xrn = options.get('geni_slice_urn', None)
    (hrn, _) = urn_to_hrn(slice_xrn)
    valid_creds = Auth.checkCredentials(credentials, 'listnodes', hrn)

    if valid_creds:
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return ""
        # get slice's hrn from options
        if slice_xrn:
            raise Exception("%s authority does not have permissions to list resources from OCF slices" %api.hrn)
        return driver.list_resources(credentials, options)
#        return ""
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[API_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListSlices(self, api, creds, options):
    #call_id = options.get('call_id')
    #if Callids().already_handled(call_id): return []
    #return self.driver.list_slices (creds, options)

    #XXX:This method shoud raise an exeption, these AM methods will only be executed by federated SMs.

    #TODO: SFAException??
    raise Exception("%s authority does not have permissions to list OCF slices" %api.hrn)
    #XXX: should this method list vms?


@rpcmethod(signature=[RSPEC_TYPE, API_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def CreateSliver(api, slice_urn, credentials, rspec, users, **kwargs):
    hrn, type = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(creds, 'createsliver', hrn)

    if valid_creds:
        return ""
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, API_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def DeleteSliver(api, slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'deletesliver', hrn)

    if valid_creds:
        return ""
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[STATUS_TYPE, API_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def SliverStatus(api, slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'sliverstatus', hrn)

    if valid_creds:
        #XXX: NO Sliver related things
        #XXX: Or shows the vm status? 

        #call_id = options.get('call_id')
        #if Callids().already_handled(call_id): return {}

        #xrn = Xrn(xrn,'slice')
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
        #return self.driver.sliver_status (slice_urn, slice_hrn)
        raise Exception("%s authority does not have permissions to list OCF slices" %api.hrn)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, API_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="sfa")
def RenewSliver(api, slice_urn, credentials, expiration_time, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'renewsliver', hrn)

    if valid_creds:
        return ""
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, API_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Shutdown(api, slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'shutdown', hrn)

    if valid_creds:
        return ""
    else:
        raise SfaInvalidArgument('Invalid Credentials')

