from django.http import *
import os, sys, logging
from openflow.common.rpc4django import rpcmethod
from openflow.common.rpc4django import *
from openflow.optin_manager.sfa.util.xrn import urn_to_hrn
from openflow.optin_manager.sfa.util.faults import SfaInvalidArgument, OCFSfaPermissionDenied, OCFSfaError
from openflow.optin_manager.sfa.util.version import version_core
from openflow.optin_manager.sfa.util.xrn import Xrn

#from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver
from openflow.optin_manager.sfa.managers.MetaSfaRegistry import MetaSfaRegistry
from openflow.optin_manager.sfa.managers.AggregateManager import AggregateManager

from openflow.optin_manager.sfa.methods.permission_manager import PermissionManager
from openflow.optin_manager.sfa.sfa_config import config as CONFIG
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
#driver = OFSfaDriver(None)
registry = MetaSfaRegistry(None)
aggregate = AggregateManager(None)
pm = PermissionManager()

@rpcmethod(signature=['string', 'string'], url_name="optin_sfa")
def ping(challenge):
    return challenge

@rpcmethod(signature=[VERSION_TYPE], url_name="optin_sfa")
def GetVersion(api=None, options={}):
    #TODO: Add complete GENI ouptut structures, GENI error codes, exceptions, etc.
    #FIXME: SFA seems not accept the error GENI structure when exceptions are rised.
    version = {'output':'', 
               'geni_api': 2, 
               'code':  {'am_type':'sfa', 
                         'geni_code':0
                        }, 
               'value': {'urn':CONFIG.URN, 
                         'hostname':CONFIG.HOSTNAME, 
                         'code_tag':CONFIG.CODE_TAG, 
                         'hrn':CONFIG.HRN, 
                         'testbed':CONFIG.TESTBED, 
                         'geni_api_versions': CONFIG.GENI_API_VERSIONS, 
                         'interface':CONFIG.INTERFACE, 
                         'geni_api':int(CONFIG.GENI_API_VERSION), 
                         'geni_ad_rspec_versions': CONFIG.GENI_AD_RSPEC_VERSIONS, 
                         'code_url': CONFIG.CODE_URL, 
                         'geni_request_rspec_versions': CONFIG.GENI_REQUEST_RSPEC_VERSIONS,
                         'sfa':int(CONFIG.SFA_VERSION), 
                         #F4F required params
                         'f4f_describe_testbed':CONFIG.DESCRIBE_TESTBED, 
                         'f4f_testbed_homepage':CONFIG.TESTBED_HOMEPAGE, 
                         'f4f_testbed_picture':CONFIG.TESTBED_PICTURE, 
                         'f4f_endorsed_tools':CONFIG.ENDORSED_TOOLS,
                        },
               } 

    return version

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def ListResources(creds, options, **kwargs):
    pm.check_permissions('ListResources',locals()) 
    #try: 
    rspec = aggregate.ListResources(options=options)
    #except Exception as e:
    #    raise OCFSfaError(e,'ListResources')
  
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.list_resources(slice_urn,slice_leaf,credentials, options)

@rpcmethod(signature=[CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def ListSlices(creds, options):
    raise Exception("SFA users do not have permission to list OCF slices")

@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="optin_sfa")
def CreateSliver(slice_xrn, creds, rspec, users, options):
    pm.check_permissions('CreateSliver',locals())    
    #try:
    rspec = aggregate.CreateSliver(slice_xrn,rspec,users,creds,options)
    #except Exception as e:
    #    raise OCFSfaError(e,'CreateSliver')
        
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.create_sliver(slice_urn,slice_leaf,authority,rspec,users,options)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def DeleteSliver(xrn, creds,options,**kwargs):
    pm.check_permissions('DeleteSliver',locals())
    #DSCredVal(slice_urn,credentials,options)
    try:
        rspec = aggregate.DeleteSliver(xrn,options)
    except Exception as e:
        raise OCFSfaError(e,'DeleteSliver')

    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.crud_slice(slice_urn,authority,credentials,action='delete_slice')


@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def SliverStatus(slice_xrn, creds, options):
    pm.check_permissions('SliverStatus',locals()) 
    #SSCredVal(slice_urn,credentials,options)
    try:
        resources = aggregate.SliverStatus(slice_xrn,options)
    except Exception as e:
        raise OCFSfaError(e,'SliverStatus')
    struct = {"geni_urn": slice_xrn, "geni_status":"ready", "geni_resources":resources}
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': struct}
    return to_return#driver.sliver_status(slice_urn,authority,credentials,options)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="optin_sfa")
def RenewSliver(slice_xrn, creds, expiration_time, **kwargs):
    #XXX: this method should extend the expiration time of the slices
    #TODO: Implement some kind of expiration date model for slices
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True} #True

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Shutdown(slice_xrn, creds, **kwargs):
    #TODO: What this method should do? Where is called?
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True} #True

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Start(xrn, creds, **kwargs):
    pm.check_permissions('Start',locals())
    try:
        slice_action = aggregate.start_slice(xrn)
    except Exception as e:
        raise OCFSfaError(e,'Start')
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action} #driver.crud_slice(slice_urn,authority,credentials,action='start_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="optin_sfa")
def Stop(xrn, creds):
    pm.check_permissions('Stop',locals())
    try:
        slice_action = aggregate.stop_slice (xrn)
    except Exception as e:
        raise OCFSfaError(e,'Stop')  
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action}#driver.crud_slice (slice_urn,authority,credentials,action='stop_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE], url_name="optin_sfa")
def reset_slice(xrn):
    xrn = Xrn(xrn)
    slice_leaf = xrn.get_leaf()
    slice_urn = xrn.get_urn()
    authority = xrn.get_authority_hrn()
    slice_action = aggregate.crud_slice (slice_urn,authority,action='reset_slice')
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action} #driver.crud_slice (slice_urn,authority,action='reset_slice')

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE], url_name="optin_sfa")
def get_trusted_certs(cred=None):
    return registry.get_trusted_certs()
