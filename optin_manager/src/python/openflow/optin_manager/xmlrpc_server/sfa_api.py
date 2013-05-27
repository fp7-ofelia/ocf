from django.http import *
import os, sys, logging
from openflow.common.rpc4django import rpcmethod
from openflow.common.rpc4django import *
from openflow.optin_manager.sfa.util.xrn import urn_to_hrn
from openflow.optin_manager.sfa.util.faults import SfaInvalidArgument

from openflow.optin_manager.sfa.util.version import version_core
from openflow.optin_manager.sfa.util.xrn import Xrn

from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver
from openflow.optin_manager.sfa.MetaSfaRegistry import MetaSfaRegistry

import zlib
# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'
driver = OFSfaDriver(None)
registry = MetaSfaRegistry(None)

@rpcmethod(signature=['string', 'string'], url_name="optin_sfa")
def ping(challenge):
    return challenge


@rpcmethod(signature=[VERSION_TYPE], url_name="optin_sfa")
def GetVersion(api=None, options={}):
    version = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': {'urn': 'urn:publicid:IDN+optin', 'hostname': 'OfeliaSDKR1', 'code_tag': '2.1-23', 'hrn': 'ocf.optin', 'testbed': 'Ofelia', 'geni_api_versions': {'2': 'http://192.168.254.170:8443/xmlrpc/sfa/'}, 'interface': 'aggregate', 'geni_api': 2, 'geni_ad_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': '/opt/ofelia/vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd'}], 'code_url': 'git://git.onelab.eu/sfa.git@sfa-2.1-23', 'geni_request_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': '/opt/ofelia/vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd'}], 'sfa': 2}}
    return version


@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def ListResources(credentials, options, **kwargs):
    slice_xrn = options.get('geni_slice_urn', None)
    if slice_xrn:
	xrn = Xrn(slice_xrn,'slice')
        slice_urn = xrn.get_urn()
        slice_leaf = xrn.get_leaf()
        options['slice'] = slice_leaf
    else:
        slice_leaf = None
        slice_urn = None
    rspec = driver.list_resources(slice_urn,slice_leaf,credentials, options)
    if options.has_key('geni_compressed') and options['geni_compressed'] == True:
        rspec = zlib.compress(rspec).encode('base64')
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.list_resources(slice_urn,slice_leaf,credentials, options)

@rpcmethod(signature=[CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def ListSlices(self, creds, options):
    raise Exception("SFA users do not have permission to list OCF slices")

@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def CreateSliver(slice_urn, credentials, rspec, users, options):
    xrn = Xrn(slice_urn, 'slice')
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    rspec = driver.create_sliver(slice_urn,slice_leaf,authority,rspec,users,options)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.create_sliver(slice_urn,slice_leaf,authority,rspec,users,options)


@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def DeleteSliver(slice_urn, credentials, **kwargs):
    xrn = Xrn(slice_urn)
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    rspec = driver.crud_slice(slice_urn,authority,credentials,action='delete_slice')
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.crud_slice(slice_urn,authority,credentials,action='delete_slice')


@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def SliverStatus(slice_urn, credentials, options):
    xrn = Xrn(slice_urn,'slice')
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    struct = driver.sliver_status(slice_urn,authority,credentials,options)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': struct}
    return to_return#driver.sliver_status(slice_urn,authority,credentials,options)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="optin_sfa")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    #XXX: this method should extend the expiration time of the slices
    #TODO: Implement some kind of expiration date model for slices
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True} #True

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Shutdown(slice_urn, credentials, **kwargs):
    #TODO: What this method should do? Where is called?
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True} #True

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Start(xrn, credentials, **kwargs):
    xrn = Xrn(xrn)
    slice_urn = xrn.get_urn()
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    slice_action = driver.crud_slice(slice_urn,authority,credentials,action='start_slice')
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action} #driver.crud_slice(slice_urn,authority,credentials,action='start_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Stop(xrn, credentials):
    xrn = Xrn(xrn)
    slice_leaf = xrn.get_leaf()
    slice_urn = xrn.get_urn()
    authority = xrn.get_authority_hrn()
    slice_action = driver.crud_slice (slice_urn,authority,credentials,action='stop_slice')
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action}#driver.crud_slice (slice_urn,authority,credentials,action='stop_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE], url_name="optin_sfa")
def reset_slice(xrn):
    xrn = Xrn(xrn)
    slice_leaf = xrn.get_leaf()
    slice_urn = xrn.get_urn()
    authority = xrn.get_authority_hrn()
    slice_action = river.crud_slice (slice_urn,authority,action='reset_slice')
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action} #driver.crud_slice (slice_urn,authority,action='reset_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE], url_name="optin_sfa")
def get_trusted_certs(cred=None):
    return registry.get_trusted_certs()
