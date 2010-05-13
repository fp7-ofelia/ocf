'''
Created on Apr 20, 2010

@author: jnaous
'''
from apps.rpc4django import rpcmethod
from decorator import decorator
import rspec as rspec_mod
from django.contrib.auth.models import User
from clearinghouse.openflow.models import OpenFlowAggregate, GAPISlice,\
    OpenFlowSwitch
from pprint import pprint
from django.conf import settings

CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

def check_cred(use_slice_urn, func, *args, **kwargs):
    from gam import CredentialVerifier
    
    func_to_privs = dict(
        ListResources=('listresources',),
        CreateSliver=('createsliver',),
        DeleteSliver=('deletesliver',),
        SliverStatus=('getsliceresources',),
    )
    cred_verif = CredentialVerifier(settings.MY_CA)
    pem_cert = kwargs['request'].META['SSL_CLIENT_CERT']
    if use_slice_urn:
        slice_urn = args[0]
        creds = args[1]
    else:
        slice_urn = None
        creds = args[0]
    priv = func_to_privs[func.func_name]
    cred_verif.verify_from_strings(
        pem_cert, creds, slice_urn, priv)
    
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

@decorator
def set_username(func, *args, **kwargs):
    '''Create the username, create the user if non-existing'''
    
    username = "%s@%s" % (kwargs['request'].META['SSL_CLIENT_S_DN_CN'],
                          kwargs['request'].META['SSL_CLIENT_I_DN_CN'])
    kwargs['username'] = username
    
@rpcmethod(signature=['string', 'string'])
def ping(str, **kwargs):
    print "************* ping called %s" % str
#    pprint(kwargs)
    return "PONG: %s" % str

@check_ssl_verify_success
@rpcmethod(signature=[VERSION_TYPE])
def GetVersion(**kwargs):
    return dict(geni_api=1)

@check_ssl_verify_success
@check_cred_no_urn
@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def ListResources(credentials, options, **kwargs):
    print "**********List resources"
    compressed = False
    if options and 'geni_compressed' in options:
        compressed  = options['geni_compressed']
    result = rspec_mod.get_all_resources()
    # return an empty rspec
    if compressed:
        import xmlrpclib
        import zlib
        result = xmlrpclib.Binary(zlib.compress(result))
    return result

@check_ssl_verify_success
@check_cred_urn
@set_username
@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def CreateSliver(slice_urn, credentials, rspec, **kwargs):
    project_name, project_desc, slice_name, slice_desc,\
    controller_url, email, password, agg_slivers \
        = rspec_mod.parse_slice(rspec)

    # create the slice in the DB
    dpids = []
    for aggregate, slivers in agg_slivers:
        for sliver in slivers:
            dpids.append(sliver['datapath_id'])

    switches = OpenFlowSwitch.objects.filter(datapath_id__in=dpids)
    gapi_slice, created = GAPISlice.objects.get_or_create(slice_urn=slice_urn)
    gapi_slice.switches.clear()
    for s in switches:
        gapi_slice.switches.add(s)
    gapi_slice.save()
    
    # make the reservation
    # TODO: concat all the responses
    for aggregate, slivers in agg_slivers:
        aggregate.client.create_slice(
            slice_urn, project_name, project_desc,
            slice_name, slice_desc, 
            controller_url,
            email, password, slivers,
        )
    
    # TODO: get the actual reserved things
    return rspec

@check_ssl_verify_success
@check_cred_urn
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def DeleteSliver(slice_urn, credentials, **kwargs):
    try:
        GAPISlice.objects.get(slice_urn=slice_urn).delete()
    except GAPISlice.DoesNotExist:
        return False
    
    for aggregate in OpenFlowAggregate.objects.all():
        aggregate.client.delete_slice(slice_urn)
    return True

@check_ssl_verify_success
@check_cred_urn
@set_username
@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def SliverStatus(slice_urn, credentials, **kwargs):
    retval = {
        'geni_urn': slice_urn,
        'geni_status': 'ready',
        'geni_resources': [],
    }
    
    # check if the slice exists   
    try:
        slice = GAPISlice.objects.get(slice_urn=slice_urn)
    except GAPISlice.DoesNotExist:
        retval['geni_status'] = 'failed'
        return retval
    
    # check the status of all switches
    for switch in slice.switches.all():
        retval['geni_resources'].append({
            'geni_urn': switch.datapath_id,
            'geni_status': 'ready' if switch.available else 'failed',
            'geni_error': '',
        })
    return retval

@check_ssl_verify_success
@check_cred_urn
@set_username
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE])
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    return False

@check_ssl_verify_success
@check_cred_urn
@set_username
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def Shutdown(slice_urn, credentials, **kwargs):
    return False
