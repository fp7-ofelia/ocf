'''
Created on Oct 2, 2010

@author: jnaous
'''
from expedient_geni import clearinghouse
from expedient.common.rpc4django.rpcdispatcher import rpcmethod

@rpcmethod(signature=["struct"], url_name="expedient_geni_ch")
def GetVersion(**kwargs):
    return clearinghouse.GetVersion()

@rpcmethod(signature=["string", "string"], url_name="expedient_geni_ch")
def CreateSlice(urn=None, **kwargs):
    return clearinghouse.CreateSlice(
        kwargs["request"].META["SSL_CLIENT_CERT"], urn)
    
@rpcmethod(signature=["string", "boolean"], url_name="expedient_geni_ch")
def DeleteSlice(urn_req, **kwargs):
    return clearinghouse.DeleteSlice(urn_req)

@rpcmethod(signature=["array"], url_name="expedient_geni_ch")
def ListAggregates(**kwargs):
    return clearinghouse.ListAggregates()

@rpcmethod(signature=["string", "string"], url_name="expedient_geni_ch")
def CreateUserCredential(user_gid, **kwargs):
    return clearinghouse.CreateUserCredential(user_gid)
