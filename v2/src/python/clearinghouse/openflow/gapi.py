'''
Created on Apr 20, 2010

@author: jnaous
'''
from rpc4djnago import rpcmethod
from gcf import gam

CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

agg_mgr = gam.AggregateManager()

@rpcmethod(signature=[VERSION_TYPE])
def GetVersion():
    return dict(geni_api=1)

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def ListResources(credentials, options):
    return agg_mgr.ListResources(credentials, options)

@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def CreateSliver(slice_urn, credentials, rspec):
    return agg_mgr.CreateSliver(slice_urn, credentials, rspec)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def DeleteSliver(slice_urn, credentials):
    return agg_mgr.DeleteSliver(slice_urn, credentials)

@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def SliverStatus(slice_urn, credentials):
    return agg_mgr.SliverStatus(slice_urn, credentials)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE])
def RenewSliver(slice_urn, credentials, expiration_time):
    return agg_mgr.RenewSliver(slice_urn, credentials, expiration_time)

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def Shutdown(slice_urn, credentials):
    return agg_mgr.Shutdown(slice_urn, credentials)
