'''
Created on Apr 20, 2010

@author: jnaous
'''
from rpc4django import rpcmethod
from gcf import gam
from decorator import decorator

CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

class Server(object): pass
agg_mgr = gam.AggregateManager()
agg_mgr._server = Server()

@decorator
def add_pem_cert(func, *args, **kwargs):
    '''decorator to add the SSL_CLIENT_CERT to agg_mgr._server'''
    agg_mgr._server.pem_cert = kwargs['request'].META['SSL_CLIENT_CERT']
    return func(*args, **kwargs)

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
    return "%s: pong" % str

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[VERSION_TYPE])
def GetVersion(**kwargs):
    return agg_mgr.GetVersion()

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def ListResources(credentials, options, **kwargs):
    return agg_mgr.ListResources(credentials, options)

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def CreateSliver(slice_urn, credentials, rspec, **kwargs):
    return agg_mgr.CreateSliver(slice_urn, credentials, rspec)

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def DeleteSliver(slice_urn, credentials, **kwargs):
    return agg_mgr.DeleteSliver(slice_urn, credentials)

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def SliverStatus(slice_urn, credentials, **kwargs):
    return agg_mgr.SliverStatus(slice_urn, credentials)

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE])
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    return agg_mgr.RenewSliver(slice_urn, credentials, expiration_time)

@check_ssl_verify_success
@add_pem_cert
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def Shutdown(slice_urn, credentials, **kwargs):
    return agg_mgr.Shutdown(slice_urn, credentials)
