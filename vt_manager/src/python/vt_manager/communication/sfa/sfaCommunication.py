from django.http import *
import os, sys, logging
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.communication.sfa.AggregateManager import *
from vt_manager.communication.sfa.auth.authManager import AuthManager
from vt_manager.communication.sfa.util.xrn import urn_to_hrn
from vt_manager.communication.sfa.util.faults import SfaInvalidArgument

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'


@rpcmethod(signature=['string', 'string'], url_name="sfa")
def ping(str, **kwargs):
    return "PONG: %s" % str


@rpcmethod(signature=[VERSION_TYPE], url_name="sfa")
def GetVersion(**kwargs):
    return AggregateManager.GetVersion(**kwargs)


@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def ListResources(credentials, options, **kwargs):
    # get slice's hrn from options    
    xrn = options.get('geni_slice_urn', '')
    (hrn, _) = urn_to_hrn(xrn)
    valid_creds = Auth.checkCredentials(credentials, 'listnodes', hrn)

    if valid_creds:
	return AggregateManager.ListResources(options)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name="sfa")
def CreateSliver(slice_urn, credentials, rspec, users, **kwargs):
    hrn, type = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(creds, 'createsliver', hrn)

    if valid_creds:
        return AggregateManager.CreateSliver(slice_urn, rspec, users, **kwargs)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def DeleteSliver(slice_urn, credentials, **kwargs):
    (hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'deletesliver', hrn)

    if valid_creds:
        return AggregateManager.DeleteSliver(slice_urn, **kwargs)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def SliverStatus(slice_urn, credentials, **kwargs):
(hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'sliverstatus', hrn)

    if valid_creds:
        return AggregateManager.SliverStatus(slice_urn, **kwargs)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE], url_name="sfa")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
(hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'renewsliver', hrn)

    if valid_creds:
        return AggregateManager.RenewSliver(slice_urn, expiration_time, **kwargs)
    else:
        raise SfaInvalidArgument('Invalid Credentials')


@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE], url_name="sfa")
def Shutdown(slice_urn, credentials, **kwargs):
(hrn, type) = urn_to_hrn(slice_urn)
    valid_creds = Auth.checkCredentials(credentials, 'shutdown', hrn)

    if valid_creds:
        return AggregateManager.ShutDown(slice_urn, **kwargs)
    else:
        raise SfaInvalidArgument('Invalid Credentials')

