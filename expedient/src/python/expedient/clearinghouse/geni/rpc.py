'''
Created on Oct 2, 2010

@author: jnaous
'''
from expedient.clearinghouse.geni import clearinghouse as geni_clearinghouse
from expedient.common.rpc4django.rpcdispatcher import rpcmethod

@rpcmethod(signature=["struct"], url_name="geni_ch")
def GetVersion(**kwargs):
    return geni_clearinghouse.GetVersion()

@rpcmethod(signature=["string", "string"], url_name="geni_ch")
def CreateSlice(urn=None, **kwargs):
    return geni_clearinghouse.CreateSlice(
        kwargs["request"].META["SSL_CLIENT_CERT"], urn)
    
@rpcmethod(signature=["string", "boolean"], url_name="geni_ch")
def DeleteSlice(urn_req, **kwargs):
    return geni_clearinghouse.DeleteSlice(urn_req)

@rpcmethod(signature=["array"], url_name="geni_ch")
def ListAggregates(**kwargs):
    return geni_clearinghouse.ListAggregates()

@rpcmethod(signature=["string", "string"], url_name="geni_ch")
def CreateUserCredential(user_gid, **kwargs):
    return geni_clearinghouse.CreateUserCredential(user_gid)
