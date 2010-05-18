'''
Created on May 15, 2010

@author: jnaous
'''

from apps.rpc4django import rpcmethod
from decorator import decorator
from optin_manager.dummyfv.models import DummyFVSlice, DummyFVDevice,\
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
@get_fv
@rpcmethod(signature=['boolean', 'string', 'string', 'string', 'string'])
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
@rpcmethod(signature=['array'])
def listDevices(**kwargs):
    return list(DummyFVDevice.objects.filter(
        fv=kwargs['fv']).values_list('dpid', flat=True))

@checkUser
@get_fv
@rpcmethod(signature=['struct', 'string'])
def getDeviceInfo(dpidStr, **kwargs):
    return {}

@checkUser 
@get_fv
@rpcmethod(signature=['array'])
def getLinks(**kwargs):
    return [{"dstDPID": link.dst_dev.dpid,
             "dstPort": link.dst_port,
             "srcDPID": link.src_dev.dpid,
             "srcPort": link.src_port} \
             for link in DummyFVLink.objects.filter(fv=kwargs['fv'])]
    
@checkUser 
@get_fv
@rpcmethod(signature=['boolean', 'string'])
def deleteSlice(sliceName, **kwargs):
    DummyFVSlice.objects.filter(
        fv=kwargs['fv']).get(sliceName).delete()
    return True

@checkUser 
@get_fv
@rpcmethod(signature=['array', 'array'])
def changeFlowSpace(changes, **kwargs):
    funcs = {"ADD": add_flowspace,
             "REMOVE": remove_flowspace,
             "CHANGE": change_flowspace}
    ret = []
    for change in changes:
        operation = change.pop("operation")
        ret.append(funcs[operation](kwargs['fv'], **change))
    
    return ret

def add_flowspace(fv, priority, dpid, match, actions):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(actions)
    for axn in axn_matches:
        try:
            slice = DummyFVSlice.objects.filter(
                fv=fv).get(name=axn.group("name"))
        except DummyFVSlice.DoesNotExist:
            raise Exception("Tried to add flowspace for non-existing " +\
                            "slice %s" % axn.group("name"))

    rule = DummyFVRule.objects.create(
        fv=fv,
        match=match,
        priority=priority,
        dpid=dpid,
        actions=actions,
    )
    
    return rule.id

def remove_flowspace(fv, id):
    rule = DummyFVRule.objects.filter(fv=fv).get(id=int(id))
    rule.delete()
    return id
    
def change_flowspace(fv, id, priority, dpid, match, actions):
    import re
    slice_re = re.compile(r"Slice:(?P<name>.+)=(?P<perms>\d+)")
    axn_matches = slice_re.findall(actions)
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
        rule = DummyFVRule.objects.filter(fv=fv).get(id=id)
    except DummyFVRule.DoesNotExist:
        raise Exception("Tried to change flowspace for non-existing " + \
                        "rule id %s" % id)

    rule.match = match
    rule.dpid = dpid
    rule.actions = actions
    rule.change_priority(priority)
    rule.save()
    return rule.id    
