'''
Created on Apr 20, 2010

@author: jnaous
'''
from apps.rpc4django import rpcmethod
import rspec as rspec_mod
from clearinghouse.openflow.models import OpenFlowAggregate, GAPISlice,\
    OpenFlowSwitch
from pprint import pprint

CREDENTIALS_TYPE = 'array' # of strings
OPTIONS_TYPE = 'struct'
RSPEC_TYPE = 'string'
VERSION_TYPE = 'struct'
URN_TYPE = 'string'
SUCCESS_TYPE = 'boolean'
STATUS_TYPE = 'struct'
TIME_TYPE = 'string'

def no_such_slice(self, slice_urn):
    import xmlrpclib
    "Raise a no such slice exception."
    fault_code = 'No such slice.'
    fault_string = 'The slice named by %s does not exist' % (slice_urn)
    raise xmlrpclib.Fault(fault_code, fault_string)
    
@rpcmethod(signature=['string', 'string'])
def ping(str, **kwargs):
    print "************* ping called %s" % str
#    pprint(kwargs)
    return "PONG: %s" % str

@rpcmethod(signature=[VERSION_TYPE])
def GetVersion(**kwargs):
    return dict(geni_api=1)

@rpcmethod(signature=[RSPEC_TYPE, CREDENTIALS_TYPE, OPTIONS_TYPE])
def ListResources(credentials, options, **kwargs):
    import base64, zlib
    print "**********List resources"

    if not options:
        options = dict()
        
    slice_urn = options.pop('geni_slice_urn', None)
    geni_available = options.pop('geni_available', True)

    print "Getting resources"
    result = rspec_mod.get_resources(slice_urn, geni_available)
    print "Done"
    # Optionally compress the result
    if 'geni_compressed' in options and options['geni_compressed']:
        result = base64.b64encode(zlib.compress(result))
    print "Returning results"
    return result

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

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def DeleteSliver(slice_urn, credentials, **kwargs):
    try:
        GAPISlice.objects.get(slice_urn=slice_urn).delete()
    except GAPISlice.DoesNotExist:
        no_such_slice(slice_urn)
    
    for aggregate in OpenFlowAggregate.objects.all():
        aggregate.client.delete_slice(slice_urn)
    return True

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
        no_such_slice(slice_urn)
    
    # check the status of all switches
    for switch in slice.switches.all():
        retval['geni_resources'].append({
            'geni_urn': switch.datapath_id,
            'geni_status': 'ready' if switch.available else 'failed',
            'geni_error': '',
        })
    return retval

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE])
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    return True

@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE])
def Shutdown(slice_urn, credentials, **kwargs):
    try:
        GAPISlice.objects.get(slice_urn=slice_urn).delete()
    except GAPISlice.DoesNotExist:
        no_such_slice(slice_urn)
    
    for aggregate in OpenFlowAggregate.objects.all():
        aggregate.client.delete_slice(slice_urn)

    return True
