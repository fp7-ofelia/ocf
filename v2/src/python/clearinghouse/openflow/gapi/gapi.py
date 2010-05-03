'''
Created on Apr 20, 2010

@author: jnaous
'''
from rpc4django import rpcmethod
from decorator import decorator
from gam import CredentialVerifier

CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

__cred_verif = CredentialVerifier()

__func_to_privs = dict(
    ListResources=('listresources',),
    CreateSliver=('createsliver',),
    DeleteSliver=('deletesliver',),
    SliverStatus=('getsliceresources',),
)

def check_cred(func, use_slice_urn, *args, **kwargs):
    pem_cert = kwargs['request'].META['SSL_CLIENT_CERT']
    if use_slice_urn:
        slice_urn = args[0]
        creds = args[1]
    else:
        slice_urn = None
        creds = args[0]
    __cred_verif.verify_from_strings(
        pem_cert, creds, slice_urn, __func_to_privs[func.func_name])
    return func(*args, **kwargs)

@decorator
def check_cred_no_urn(func, *args, **kwargs):
    return check_cred(False, func, *args, **kwargs)

@decorator
def check_cred_urn(func, *args, **kwargs):
    return check_cred(True, func, *args, **kwargs)

@decorator
def check_ssl_verify_success(func, *args, **kwargs):
    '''Make sure that SSL_VERIFY_CLIENT is SUCCESS'''
    verify = kwargs['request'].META['SSL_CLIENT_VERIFY']
    if verify == "SUCCESS":
        return func(*args, **kwargs)
    else:
        return "ERROR Client Certificate Validation: %s" % verify

@rpcmethod(signature=['string', 'string'])
def ping(str):
    print "************* ping called %s" % str
    return "PONG: %s" % str

@check_ssl_verify_success
@rpcmethod(signature=[VERSION_TYPE])
def GetVersion(**kwargs):
    return dict(geni_api=1)

@check_ssl_verify_success
@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
@check_cred_no_urn
def ListResources(credentials, options, **kwargs):
    return agg_mgr.ListResources(credentials, options)

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def CreateSliver(slice_urn, credentials, rspec, **kwargs):
    return agg_mgr.CreateSliver(slice_urn, credentials, rspec)

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def DeleteSliver(slice_urn, credentials, **kwargs):
    return agg_mgr.DeleteSliver(slice_urn, credentials)

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def SliverStatus(slice_urn, credentials, **kwargs):
    return agg_mgr.SliverStatus(slice_urn, credentials)

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE])
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    return agg_mgr.RenewSliver(slice_urn, credentials, expiration_time)

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def Shutdown(slice_urn, credentials, **kwargs):
    return agg_mgr.Shutdown(slice_urn, credentials)
