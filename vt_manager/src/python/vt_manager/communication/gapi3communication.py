from django.http import *
import os, sys, logging
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
#from vt_manager.communication.geni.v3.configurators.handlerconfigurator import HandlerConfigurator

#URL_NAME
GAPI3_URL = "gapi"

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

#handler = HandlerConfigurator()
#handler.configure_handler()

@rpcmethod(signature=['string', 'string'], url_name=GAPI3_URL)
def ping(challenge):
    return challenge

@rpcmethod(signature=[VERSION_TYPE], url_name=GAPI3_URL)
def GetVersion(api=None, options={}):
    #return handler.get_vt_am_delegate().get_resources()
    return None

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def ListResources(credentials, options):
    return None

@rpcmethod(signature=[RSPEC_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def Describe(urns, credentials, options):
    return None

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, RSPEC_TYPE ,OPTIONS_TYPE], url_name=GAPI3_URL)
def Allocate(slice_urn, credentials, rspec, options):
    return None

@rpcmethod(signature=[RSPEC_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def Provision(urns, creds, options):
    return None 

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE], url_name=GAPI3_URL)
def Delete(urns, creds, options):
    return None

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, ACTION_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def PerformOperationalAction(urns, creds, action, options):
    return None

@rpcmethod(signature=[STATUS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def Status(urns, creds, options):
    return None 

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, TIME_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def Renew(urns, creds, expiration_time, options):
    return None

@rpcmethod(signature=[SUCCESS_TYPE, URNS_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE], url_name=GAPI3_URL)
def Shutdown(urns, creds):
    return None 

