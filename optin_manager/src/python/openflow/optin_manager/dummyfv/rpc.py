'''
Created on May 15, 2010

@author: jnaous
'''
from pprint import pprint
from expedient.common.rpc4django import rpcmethod
from decorator import decorator
from openflow.optin_manager.dummyfv.models import DummyFVSlice, DummyFVDevice,\
    DummyFVLink, DummyFVRule, DummyFV
from django.contrib.auth.models import User

@decorator
def get_fv(func, *args, **kwargs):
    """
    Add a 'fv' keyword pointing to the flowvisor responsible fore this call.
    """
    fv_id = kwargs['fv_id']
    fv = DummyFV.objects.get(id=fv_id)
    kwargs['fv'] = fv
    return func(*args, **kwargs)

@decorator
def checkUser(func, *args, **kwargs):
    """
    Check that the user is authenticated and known.
    """
    if "request" not in kwargs:
        raise Exception("Request not available for XML-RPC %s" % \
                        func.func_name)
        
    if not hasattr(kwargs["request"], "user"):
        raise Exception("Authentication Middleware not installed in settings.")        

    if not kwargs['request'].user.is_authenticated():
        raise Exception("ERROR: %s: Unauthenticated user!" % func.func_name)
    else:
        kwargs['user'] = kwargs['request'].user
        return func(*args, **kwargs)

@checkUser
@get_fv
@rpcmethod(name="api.createSlice", url_name="dummyfv_rpc",
           signature=['boolean', 'string', 'string', 'string', 'string'])
def createSlice(sliceName, passwd, controller_url, slice_email, **kwargs):
    slice = DummyFVSlice.objects.create(fv=kwargs['fv'],
                                name=sliceName, password=passwd,
                                controller_url=controller_url,
                                email=slice_email)
    print "FV created slice name=%s, password=%s, url=%s, email=%s" % (
        slice.name, slice.password, slice.controller_url, slice.email,
    )
    return True

@checkUser 
@get_fv
@rpcmethod(name="api.listDevices", url_name="dummyfv_rpc",
           signature=['array'])
def listDevices(**kwargs):
    return list(DummyFVDevice.objects.filter(
        fv=kwargs['fv']).values_list('dpid', flat=True))

@checkUser
@get_fv
@rpcmethod(name="api.getDeviceInfo", url_name="dummyfv_rpc",
           signature=['struct', 'string'])
def getDeviceInfo(dpidStr, **kwargs):
    return {}

@checkUser 
@get_fv
@rpcmethod(name="api.getLinks", url_name="dummyfv_rpc",
           signature=['array'])
def getLinks(**kwargs):
    return [{"dstDPID": link.dst_dev.dpid,
             "dstPort": link.dst_port,
             "srcDPID": link.src_dev.dpid,
             "srcPort": link.src_port} \
             for link in DummyFVLink.objects.filter(fv=kwargs['fv'])]
    
@checkUser 
@get_fv
@rpcmethod(name="api.deleteSlice", url_name="dummyfv_rpc",
           signature=['boolean', 'string'])
def deleteSlice(sliceName, **kwargs):
    DummyFVSlice.objects.filter(
        fv=kwargs['fv']).get(name=sliceName).delete()
    return True


@checkUser 
@get_fv
@rpcmethod(name="api.ping", url_name="dummyfv_rpc",
           signature=['string', 'string'])
def ping(data, **kwargs):
    return "PONG: %s"%(data)

@checkUser 
@get_fv
@rpcmethod(name="api.changeFlowSpace", url_name="dummyfv_rpc",
           signature=['array', 'array'])
def changeFlowSpace(changes, **kwargs):
    funcs = {"ADD": add_flowspace,
             "REMOVE": remove_flowspace,
             "CHANGE": change_flowspace}
    ret = []
    for change in changes:
        operation = change.pop("operation")
        result = funcs[operation](kwargs['fv'], change)
        ret.append(result)
    return ret

def add_flowspace(fv, change):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(change['actions'])
    for axn in axn_matches:
        try:
            slice = DummyFVSlice.objects.filter(
                fv=fv).get(name=axn.group("name"))
        except DummyFVSlice.DoesNotExist:
            raise Exception("Tried to add flowspace for non-existing " +\
                            "slice %s" % axn.group("name"))
    rule = DummyFVRule(
        fv=fv,
        match=change['match'],
        priority=int(change['priority']),
        dpid=change['dpid'],
        actions=change['actions'],
    )
    rule.save()
    return rule.id

def remove_flowspace(fv, change):
    id = change['id']
    rule = DummyFVRule.objects.filter(fv=fv).get(id=int(id))
    rule.delete()
    return id
    
def change_flowspace(fv, change):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(change['actions'])
    for axn in axn_matches:
        try:
            slice = DummyFVSlice.objects.filter(
                fv=fv).get(name=axn.group("name"))
        except DummyFVSlice.DoesNotExist:
            raise Exception(
                "Tried to change flowspace for non-existing slice %s" %\
                axn.group("name")
            )
    try:
        rule = DummyFVRule.objects.filter(fv=fv).get(id=change['id'])
    except DummyFVRule.DoesNotExist:
        raise Exception("Tried to change flowspace for non-existing " + \
                        "rule id %s" % change['id'])

    rule.match = change['match']
    rule.dpid = change['dpid']
    rule.actions = change['actions']
    rule.priority = int(change['priority'])
    rule.save()
    return rule.id    
