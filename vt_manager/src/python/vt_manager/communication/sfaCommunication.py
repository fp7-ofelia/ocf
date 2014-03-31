from django.http import *
import os, sys, logging
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.communication.sfa.util.xrn import urn_to_hrn
from vt_manager.communication.sfa.util.faults import SfaInvalidArgument

from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.methods.permission_manager import PermissionManager
from vt_manager.communication.sfa.managers.AggregateManager import AggregateManager
#from vt_manager.communication.sfa.drivers.VTSfaDriver import VTSfaDriver
from vt_manager.communication.sfa.sfa_config import config as CONFIG

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'
#driver = VTSfaDriver(None)
aggregate = AggregateManager()
pm = PermissionManager()
@rpcmethod(signature=['string', 'string'], url_name="sfa")
def ping(challenge):
    return challenge

@rpcmethod(signature=[VERSION_TYPE], url_name="sfa")
def GetVersion():
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

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListResources(credentials, options, **kwargs):
    pm.check_permissions('ListResources',locals())
    rspec = aggregate.ListResources(options,**kwargs)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return 

@rpcmethod(signature=[CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListSlices(self, creds, options):
    #TODO: SFAException??
    #XXX: should this method list vms?
    return ""

@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def CreateSliver(slice_xrn, creds, rspec, users, options):
    pm.check_permissions('CreateSliver',locals())
    rspec = aggregate.CreateSliver(slice_xrn,rspec,users,creds,options)
    #xrn = Xrn(slice_urn, 'slice')
    #slice_leaf = xrn.get_leaf()
    #authority = xrn.get_authority_hrn()
    #rspec = driver.create_sliver(slice_leaf,authority,rspec,users,options)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    return to_return #driver.create_sliver(slice_urn,slice_leaf,authority,rspec,users,options)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def DeleteSliver(xrn, creds, options={},**kwargs):
    pm.check_permissions('DeleteSliver',locals())
    flag = aggregate.DeleteSliver(xrn,options)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': flag}
    return to_return #driver.crud_slice(slice_urn,authority,credentials,action='delete_slice')


@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def SliverStatus(slice_xrn, creds, options):
    #xrn = Xrn(slice_urn,'slice')
    #slice_leaf = xrn.get_leaf()
    #authority = xrn.get_authority_hrn()
    pm.check_permissions('SliverStatus',locals())
    struct = aggregate.SliverStatus(slice_xrn,options)
    to_return = {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': struct}
    return to_return#driver.sliver_status(slice_urn,authority,credentials,options)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="sfa")
def RenewSliver(slice_xrn, creds, expiration_time, **kwargs):
    pm.check_permissions('RenewSliver',locals())
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True}

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Shutdown(slice_xrn, creds, **kwargs):
    pm.check_permissions('ShutDown',locals())
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': True}

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Start(xrn, creds, **kwargs):
    pm.check_permissions('Start',locals())
    slice_action = aggregate.start_slice(xrn)
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action}

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Stop(xrn, creds):
    pm.check_permissions('Stop',locals())
    slice_action = aggregate.stop_slice(xrn)
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action}

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE], url_name="sfa")
def reset_slice(xrn):
    slice_action = aggregate.reset_slice(xrn)
    return {'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': slice_action}
