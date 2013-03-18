from django.http import *
import os, sys, logging
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.communication.sfa.authManager import AuthManager
from vt_manager.communication.sfa.util.xrn import urn_to_hrn
from vt_manager.communication.sfa.util.faults import SfaInvalidArgument
from vt_manager.communication.sfa.trust.auth import Auth

from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.callids import Callids

from vt_manager.communication.sfa.VTSfaDriver import VTSfaDriver

#Only for testing before the methods are implemented in VTSfaDriver
#from vt_manager.communication.sfa.AggregateManager import AggregateManager

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'
driver = VTSfaDriver(None)
auth = Auth(None, None)

@rpcmethod(signature=['string', 'string'], url_name="sfa")
def ping(challenge):
    return challenge


@rpcmethod(signature=[VERSION_TYPE], url_name="sfa")
def GetVersion():
   # xrn=Xrn(api.hrn)
   # version = version_core()
   # version_generic = {
   #     'interface':'aggregate',
   #     'sfa': 2,
   #     'geni_api': 2,
   #     'geni_api_versions': '2',#: 'http://%s:%s' % (api.config.SFA_AGGREGATE_HOST, api.config.SFA_AGGREGATE_PORT)},
    #    'hrn':xrn.get_hrn(),
    #    'urn':xrn.get_urn(),
    #}
    #version.update(version_generic)
 #   testbed_version = driver.aggregate_version()
 #   version.update(testbed_version)
    version = {'urn': 'urn:publicid:IDN+top+dummy', 'hostname': 'OfeliaSDKr1', 'code_tag': '2.1-23', 'hrn': 'top.dummy', 'testbed': 'Ofelia', 'geni_api_versions': {'2': 'http://192.168.254.170:8445'}, 'interface': 'aggregate', 'geni_api': 2, 'geni_ad_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': '/opt/ofelia/vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd'}], 'code_url': 'git://git.onelab.eu/sfa.git@sfa-2.1-23', 'geni_request_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': '/opt/ofelia/vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd'}], 'sfa': 2}

    return version


@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListResources(credentials, options, **kwargs):
    # get slice's hrn from options    
    slice_xrn = options.get('geni_slice_urn', None)
    (hrn, _) = urn_to_hrn(slice_xrn)
#    valid_creds = auth.checkCredentials(credentials, 'listnodes', hrn)

#    if valid_creds:
#    call_id = options.get('call_id')
#    if Callids().already_handled(call_id): return ""
        # get slice's hrn from options
#        if slice_xrn:
#            raise Exception("authority does not have permissions to list resources from OCF slices")
#        return ""#driver.list_resources(options)
#        return ""
#    else:
#        raise SfaInvalidArgument('Invalid Credentials')
    return driver.list_resources(credentials, options)

@rpcmethod(signature=[CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListSlices(self, creds, options):
    #call_id = options.get('call_id')
    #if Callids().already_handled(call_id): return []
    #return self.driver.list_slices (creds, options)

    #XXX:This method shoud raise an exeption, these AM methods will only be executed by federated SMs.

    #TODO: SFAException??
    #XXX: should this method list vms?
    return ""

@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def CreateSliver(slice_urn, credentials, rspec, users, **kwargs):
    hrn, type = urn_to_hrn(slice_urn)
    return ""#am.CreateSliver(sliver_urn, rspec, users)

#XXX: deletesliver means delete all the slivers assigned to a slice
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def DeleteSliver(slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    return driver.delete_slice(slice_urn)

@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def SliverStatus(slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    #XXX: NO Sliver related things
    #XXX: Or shows the vm status? 

    #call_id = options.get('call_id')
    #if Callids().already_handled(call_id): return {}

    #xrn = Xrn(xrn,'slice')
    #slice_urn=xrn.get_urn()
    #slice_hrn=xrn.get_hrn()
    #return self.driver.sliver_status (slice_urn, slice_hrn)
    return ""

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="sfa")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    return ""

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Shutdown(slice_urn, credentials, **kwargs):
    return ""
