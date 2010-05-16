'''
Created on May 15, 2010

@author: jnaous
'''

from apps.rpc4django import rpcmethod
from decorator import decorator
from optin_manager.dummyfv.models import DummyFVSlice, DummyFVDevice,\
    DummyFVLink, DummyFVRule
from django.contrib.auth.models import User

@decorator
def checkUser(func, *args, **kwargs):
    if "request" not in kwargs:
        raise Exception("Request not available for XML-RPC %s" % \
                        func.func_name)
    meta = kwargs["request"].META
    if "REMOTE_USER" not in meta:
        raise Exception("Remote user not authenticated for XML-RPC %s." %\
                        func.func_name)
    if User.objects.filter(username=meta["REMOTE_USER"]).count() == 0:
       raise Exception("Remote user %s is unknown for call %s." % (
            meta["REMOTE_USER"], func.func_name)
       )
       
    return func(*args, **kwargs)

@checkUser 
@rpcmethod(signature=['boolean', 'string', 'string', 'string', 'string'])
def createSlice(sliceName, passwd, controller_url, slice_email, **kwargs):
    DummyFVSlice.objects.create(name=sliceName, password=passwd,
                                controller_url=controller_url,
                                email=slice_email)
    return True

@checkUser 
@rpcmethod(signature=['array'])
def listDevices(**kwargs):
    return DummyFVDevice.objects.values_list('dpid', flat=True)

@checkUser 
@rpcmethod(signature=['array'])
def getLinks(**kwargs):
    return [{"dstDPID": link.dst_dev.dpid,
             "dstPort": link.dst_port,
             "srcDPID": link.src_dev.dpid,
             "srcPort": link.src_port} for link in DummyFVLink.objects.all()]
    
@checkUser 
@rpcmethod(signature=['boolean', 'string'])
def deleteSlice(sliceName, **kwargs):
    DummyFVSlice.objects.get(sliceName).delete()
    return True

@checkUser 
@rpcmethod(signature=['array', 'array'])
def changeFlowSpace(changes, **kwargs):
    funcs = {"ADD": add_flowspace,
             "REMOVE": remove_flowspace,
             "CHANGE": change_flowspace}
    ret = []
    for change in changes:
        operation = change.pop("operation")
        ret.append(funcs[operation](**change))
    
    return ret

def add_flowspace(priority, dpid, match, actions):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(actions)
    for axn in axn_matches:
        try:
            slice = DummyFVSlice.objects.get(name=axn.group("name"))
        except DummyFVSlice.DoesNotExist:
            print "Tried to add flowspace for non-existing slice %s" %\
                axn.group("name")
            return -1

    rule = DummyFVRule.objects.create(
        match=match,
        priority=priority,
        dpid=dpid,
        actions=actions,
    )
    
    return rule.id

def remove_flowspace(id):
    try:
        rule = DummyFVRule.objects.get(id=int(id))
    except DummyFVRule.DoesNotExist:
        return -1
    else:
        rule.delete()
        return id
    
def change_flowspace(id, priority, dpid, match, actions):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(actions)
    for axn in axn_matches:
        try:
            slice = DummyFVSlice.objects.get(name=axn.group("name"))
        except DummyFVSlice.DoesNotExist:
            print "Tried to change flowspace for non-existing slice %s" %\
                axn.group("name")
            return -1

    try:
        rule = DummyFVRule.objects.get(id=id)
    except DummyFVRule.DoesNotExist:
        print "Tried to change flowspace for non-existing rule id %s" % id
        return -1

    rule.match = match
    rule.dpid = dpid
    rule.actions = actions
    rule.change_priority(priority)
    rule.save()
    return rule.id    
