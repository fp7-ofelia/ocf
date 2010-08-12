'''
Created on Apr 20, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
import rspec as rspec_mod
from openflow.plugin.models import OpenFlowAggregate, GAPISlice, OpenFlowSwitch
import logging
from gcf.geni import CredentialVerifier
from django.conf import settings
from decorator import decorator

logger = logging.getLogger("openflow.plugin.gapi")

# Parameter Types
CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

# SFA permissions mapping
PRIVS_MAP = dict(
    ListResources=(),
    RenewSliver=('renewsliver',),
    CreateSliver=('createsliver',),
    DeleteSliver=('deleteslice',),
    SliverStatus=('getsliceresources',),
)

cred_verifier = CredentialVerifier(settings.GCF_X509_CERT_DIR)

def no_such_slice(self, slice_urn):
    import xmlrpclib
    "Raise a no such slice exception."
    fault_code = 'No such slice.'
    fault_string = 'The slice named by %s does not exist' % (slice_urn)
    raise xmlrpclib.Fault(fault_code, fault_string)

def require_creds(use_slice_urn):
    """Decorator to verify credentials"""
    def require_creds(func, *args, **kw):
        
        client_cert = kw["request"].META["SSL_CLIENT_CERT"]

        if use_slice_urn:
            slice_urn = args[0]
            credentials = args[1]
        else:
            slice_urn = None
            credentials = args[0]
            
        cred_verifier.verify_from_strings(
            client_cert, credentials,
            slice_urn, PRIVS_MAP[func.func_name])
        
        return func(*args, **kw)
        
    return decorator(require_creds)
    
@rpcmethod(signature=['string', 'string'], url_name="openflow_gapi")
def ping(str, **kwargs):
    return "PONG: %s" % str

@rpcmethod(signature=[VERSION_TYPE], url_name="openflow_gapi")
def GetVersion(**kwargs):
    logger.debug("Called GetVersion")
    return dict(geni_api=1)

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE],
           url_name="openflow_gapi")
@require_creds(False)
def ListResources(credentials, options, **kwargs):
    import base64, zlib

    logger.debug("Called ListResources")

    if not options:
        options = dict()
        
    slice_urn = options.pop('geni_slice_urn', None)
    geni_available = options.pop('geni_available', True)

    result = rspec_mod.get_resources(slice_urn, geni_available)

    # Optionally compress the result
    if 'geni_compressed' in options and options['geni_compressed']:
        logger.debug("Compressing rspec")
        result = base64.b64encode(zlib.compress(result))

    return result

@require_creds(True)
@rpcmethod(signature=[RSPEC_TYPE, URN_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE],
           url_name="openflow_gapi")
def CreateSliver(slice_urn, credentials, rspec, users, **kwargs):

    logger.debug("Called CreateSliver")

    project_name, project_desc, slice_name, slice_desc,\
    controller_url, email, password, agg_slivers \
        = rspec_mod.parse_slice(rspec)

    logger.debug("Parsed Rspec")

    # create the slice in the DB
    dpids = []
    for aggregate, slivers in agg_slivers:
        for sliver in slivers:
            dpids.append(sliver['datapath_id'])

    switches = OpenFlowSwitch.objects.filter(datapath_id__in=dpids)
    
    logger.debug("Slivers: %s" % agg_slivers)
    
    # make the reservation
    # TODO: concat all the responses
    for aggregate, slivers in agg_slivers:
        print "creating slice at aggregate."
        try:
            aggregate.client.proxy.create_slice(
                slice_urn, project_name, project_desc,
                slice_name, slice_desc, 
                controller_url,
                email, password, slivers,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Could not reserve slice. Got message '%s' from\
the opt-in manager at %s" % (e, str(aggregate.client.url)))
    
    gapi_slice, created = GAPISlice.objects.get_or_create(slice_urn=slice_urn)
    
    gapi_slice.switches.clear()
    for s in switches:
        gapi_slice.switches.add(s)
    gapi_slice.save()
    
    logger.debug("Done creating sliver")

    # TODO: get the actual reserved things
    return rspec

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def DeleteSliver(slice_urn, credentials, **kwargs):
    for aggregate in OpenFlowAggregate.objects.all():
        try:
            aggregate.client.proxy.delete_slice(slice_urn)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Could not delete slice. Got message '%s' from\
the opt-in manager at %s" % (e, aggregate.client.url))

    try:
        GAPISlice.objects.get(slice_urn=slice_urn).delete()
    except GAPISlice.DoesNotExist:
        no_such_slice(slice_urn)
    
    return True

@require_creds(True)
@rpcmethod(signature=[STATUS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
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
        no_such_slice(slice_urn)
    
    # check the status of all switches
    for switch in slice.switches.all():
        retval['geni_resources'].append({
            'geni_urn': switch.datapath_id,
            'geni_status': 'ready' if switch.available else 'failed',
            'geni_error': '',
        })
    return retval

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE],
           url_name="openflow_gapi")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    return True

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def Shutdown(slice_urn, credentials, **kwargs):
    for aggregate in OpenFlowAggregate.objects.all():
        try:
            aggregate.client.proxy.delete_slice(slice_urn)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Could not shutdown slice. Got message '%s' from\
the opt-in manager at %s" % (e, aggregate.client.url))

    try:
        GAPISlice.objects.get(slice_urn=slice_urn).delete()
    except GAPISlice.DoesNotExist:
        no_such_slice(slice_urn)

    return True
