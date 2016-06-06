from django.http import *
import os, sys, logging
from openflow.common.rpc4django import rpcmethod
from openflow.common.rpc4django import *


from openflow.optin_manager.geni.v3.configurators.optin import HandlerConfigurator

#URL_NAME
GAPI3_URL = "gapi3"

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'
URNS_TYPE = 'string'
ACTION_TYPE = 'string'
CERT_TYPE = 'string'

handler  = HandlerConfigurator.configure_handler()

@rpcmethod(signature=['string', 'string'], url_name=GAPI3_URL)
def ping(challenge):
    return challenge

@rpcmethod(signature=[VERSION_TYPE], url_name=GAPI3_URL)
def GetVersion(options={}):
    return handler.GetVersion(options)

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def ListResources(credentials, options, caller_cert=None):
    return handler.ListResources(credentials, options, caller_cert)

@rpcmethod(signature=[RSPEC_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Describe(urns, credentials, options, caller_cert=None):
    return handler.Describe(urns, credentials, options, caller_cert)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, RSPEC_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Allocate(slice_urn, credentials, rspec, options, caller_cert=None):
    return handler.Allocate(slice_urn, credentials, rspec, options, caller_cert)

@rpcmethod(signature=[RSPEC_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Provision(urns, creds, options, caller_cert=None):
    return handler.Provision(urns, creds, options, caller_cert)

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Delete(urns, creds, options, caller_cert=None):
    return handler.Delete(urns, creds, options, caller_cert)

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, ACTION_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def PerformOperationalAction(urns, creds, action, options, caller_cert=None):
    return handler.PerformOperationalAction(urns, creds, action, options, caller_cert)

@rpcmethod(signature=[STATUS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Status(urns, creds, options, caller_cert=None):
    return handler.Status(urns, creds, options, caller_cert)

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, TIME_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Renew(urns, creds, expiration_time, options, caller_cert=None):
    return handler.Renew(urns, creds, expiration_time, options, caller_cert)

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE, CERT_TYPE], url_name=GAPI3_URL)
def Shutdown(urns, creds, caller_cert=None):
    return handler.Shutdown(urns, creds, caller_cert)

