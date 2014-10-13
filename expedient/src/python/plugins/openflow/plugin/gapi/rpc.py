'''
Created on Oct 1, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
import xmlrpclib
import logging
from expedient.common.federation.geni.util.cred_util import CredentialVerifier
from django.conf import settings
from decorator import decorator
from openflow.plugin.gapi import gapi
from expedient.clearinghouse.slice.models import Slice
from openflow.plugin.gapi.gapi import DuplicateSliceNameException

logger = logging.getLogger("openflow.plugin.gapi.rpc")

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

# SFA permissions mapping
PRIVS_MAP = dict(
    ListResources=(),
    RenewSliver=('renewsliver',),
    CreateSliver=('createsliver',),
    DeleteSliver=('deleteslice',),
    SliverStatus=('getsliceresources',),
    Shutdown=('shutdown',),
)

def no_such_slice(slice_urn):
    "Raise a no such slice exception."
    fault_code = 'No such slice.'
    fault_string = 'The slice named by %s does not exist' % (slice_urn)
    raise xmlrpclib.Fault(fault_code, fault_string)

def duplicate_slice_name(slice_name):
    "Raise duplicate slice name exception."
    fault_code = "Duplicate slice name."
    fault_string = "The slice name is already in use. Please choose a" \
        " different slice name."
    raise xmlrpclib.Fault(fault_code, fault_string)

def require_creds(use_slice_urn):
    """Decorator to verify credentials"""
    def require_creds(func, *args, **kw):
        
        logger.debug("Checking creds")
        
        client_cert = kw["request"].META["SSL_CLIENT_CERT"]

        if use_slice_urn:
            slice_urn = args[0]
            credentials = args[1]
        else:
            slice_urn = None
            credentials = args[0]
            
        cred_verifier = CredentialVerifier(settings.GCF_X509_TRUSTED_CERT_DIR)
            
        cred_verifier.verify_from_strings(
            client_cert, credentials,
            slice_urn, PRIVS_MAP[func.func_name])

        logger.debug("Creds pass")
        
        return func(*args, **kw)
        
    return decorator(require_creds)
    
@rpcmethod(signature=['string', 'string'], url_name="openflow_gapi")
def ping(str, **kwargs):
    return "PONG: %s" % str

@rpcmethod(signature=[VERSION_TYPE], url_name="openflow_gapi")
def GetVersion(**kwargs):
    logger.debug("Called GetVersion")
    return gapi.GetVersion()

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE],
           url_name="openflow_gapi")
@require_creds(False)
def ListResources(credentials, options, **kwargs):
    logger.debug("Called ListResources")
    return gapi.ListResources(options, kwargs["request"].user)

@require_creds(True)
@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE],
           url_name="openflow_gapi")
def CreateSliver(slice_urn, credentials, rspec, users, **kwargs):
    logger.debug("Called CreateSliver for user %s" % kwargs["request"].user)
    try:
        return gapi.CreateSliver(slice_urn, rspec, kwargs["request"].user)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)
    except DuplicateSliceNameException as e:
        duplicate_slice_name(e.slice_name)
    
@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def DeleteSliver(slice_urn, credentials, **kwargs):
    logger.debug("Called DeleteSliver")
    try:
        return gapi.DeleteSliver(slice_urn, kwargs["request"].user)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)

@require_creds(True)
@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def SliverStatus(slice_urn, credentials, **kwargs):
    logger.debug("Called SliverStatus")
    try:
        return gapi.SliverStatus(slice_urn)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)
        
@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE],
           url_name="openflow_gapi")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    logger.debug("Called RenewSliver")
    try:
        return gapi.RenewSliver(slice_urn, expiration_time)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)
    
@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def Shutdown(slice_urn, credentials, **kwargs):
    logger.debug("Called Shutdown")
    try:
        return gapi.Shutdown(slice_urn, kwargs["request"].user)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)
