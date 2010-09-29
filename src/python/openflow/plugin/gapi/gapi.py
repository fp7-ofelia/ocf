'''
Created on Apr 20, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
import xmlrpclib
import rspec as rspec_mod
from openflow.plugin.models import GAPISlice,\
    OpenFlowSliceInfo, OpenFlowInterfaceSliver,\
    FlowSpaceRule
import logging
from geni import CredentialVerifier
from django.conf import settings
from django.test import Client
from decorator import decorator
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.project.models import Project
from django.core.urlresolvers import reverse
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.utils import create_or_update
from django.utils.importlib import import_module
from django.http import HttpRequest
from django.contrib.auth import login

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

def fake_login(client, user):
    engine = import_module(settings.SESSION_ENGINE)

    # Create a fake request to store login details.
    request = HttpRequest()
    if client.session:
        request.session = client.session
    else:
        request.session = engine.SessionStore()
    login(request, user)

    # Save the session values.
    request.session.save()

    # Set the cookie to represent the session.
    session_cookie = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie] = request.session.session_key
    cookie_data = {
        'max-age': None,
        'path': '/',
        'domain': settings.SESSION_COOKIE_DOMAIN,
        'secure': settings.SESSION_COOKIE_SECURE or None,
        'expires': None,
    }
    client.cookies[session_cookie].update(cookie_data)


def no_such_slice(slice_urn):
    "Raise a no such slice exception."
    fault_code = 'No such slice.'
    fault_string = 'The slice named by %s does not exist' % (slice_urn)
    raise xmlrpclib.Fault(fault_code, fault_string)

def get_slice(slice_urn):
    # get the slice
    try:
        slice = Slice.objects.get(gapislice__slice_urn=slice_urn)
    except Slice.DoesNotExist:
        no_such_slice(slice_urn)
    return slice

def require_creds(use_slice_urn):
    """Decorator to verify credentials"""
    def require_creds(func, *args, **kw):
        
        logger.debug("Checking creds")
        
        client_cert = kw["request"].META["SSL_CLIENT_CERT"]

        if use_slice_urn:
            slice_urn = args[0]
            credentials = args[1]
        else:
            slice_urn = None
            credentials = args[0]
            
        cred_verifier = CredentialVerifier(settings.GCF_X509_CERT_DIR)
            
        cred_verifier.verify_from_strings(
            client_cert, credentials,
            slice_urn, PRIVS_MAP[func.func_name])

        logger.debug("Creds pass")
        
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

    if slice_urn:
        get_slice(slice_urn)

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
    controller_url, email, password, slivers \
        = rspec_mod.parse_slice(rspec)

    logger.debug("Parsed Rspec")

    user = kwargs['request'].user
    give_permission_to("can_create_project", Project, user)

    client = Client()
    fake_login(client, user)
    
    logger.debug("Creating/updating project")
    
    # check if the project exists create otherwise
    try:
        project = Project.objects.get(name=project_name)
        project.description = project_desc
        project.save()
    except Project.DoesNotExist:
        test_get_and_post_form(
            client, url=reverse("project_create"),
            params={"name": project_name, "description": project_desc}
        )
        project = Project.objects.get(name=project_name)

    logger.debug("Creating/updating slice")

    # get or create slice in the project
    try:
        slice = Slice.objects.get(name=slice_name)
        slice.description = slice_desc
        slice.save()
    except Slice.DoesNotExist:
        test_get_and_post_form(
            client, url=reverse("slice_create", args=[project.id]),
            params={"name": slice_name, "description": slice_desc}
        )
        slice = Slice.objects.get(name=slice_name)

    logger.debug("Creating/updating slice info")
    
    # create openflow slice info for the slice
    create_or_update(
        OpenFlowSliceInfo,
        filter_attrs={"slice": slice},
        new_attrs={
            "controller_url": controller_url,
            "password": password,
        },
    )
    
    logger.debug("creating gapislice")

    # store a pointer to this slice using the slice_urn
    GAPISlice.objects.get_or_create(slice_urn=slice_urn, slice=slice)
    
    logger.debug("adding resources")

    sliver_ids = []
    for iface, fs_set in slivers.items():
        # give the user, project, slice permission to use the aggregate
        aggregate = iface.aggregate.as_leaf_class()
        give_permission_to("can_use_aggregate", aggregate, user)
        give_permission_to("can_use_aggregate", aggregate, project)
        give_permission_to("can_use_aggregate", aggregate, slice)

        # make sure all the selected interfaces are added
        sliver, _ = OpenFlowInterfaceSliver.objects.get_or_create(
            slice=slice, resource=iface)
        sliver_ids.append(sliver.id)
        
        # delete and recreate the flowspace again
        FlowSpaceRule.objects.filter(sliver=sliver).delete()
        for fs in fs_set:
            FlowSpaceRule.objects.create(sliver=sliver, **fs)
    
    logger.debug("Deleting old resources")

    # Delete all removed interfaces
    OpenFlowInterfaceSliver.objects.exclude(id__in=sliver_ids).delete()
        
    logger.debug("Starting the slice %s %s" % (slice, slice.name))
    
    # make the reservation
    # TODO: concat all the responses
    client.post(reverse("slice_start", args=[slice.id]))
    
    logger.debug("Done creating sliver")

    client.logout()

    # TODO: get the actual reserved things
    return rspec

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def DeleteSliver(slice_urn, credentials, **kwargs):
    slice = get_slice(slice_urn)
    client = Client()
    fake_login(client, kwargs["request"].user)
    client.post(reverse("slice_delete", args=[slice.id]))
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
    
    slice = get_slice(slice_urn)
        
    for of_sliver in OpenFlowInterfaceSliver.objects.filter(slice=slice):
        if of_sliver.resource.available:
            stat = "ready"
            err = "" 
        else:
            stat = "failed"
            err = "Unavailable since %s"  \
                % of_sliver.resource.status_change_timestamp

        iface = of_sliver.resource.as_leaf_class()
        retval['geni_resources'].append({
            'geni_urn': rspec_mod._port_to_urn(
                    iface.switch.datapath_id, iface.port_num),
            'geni_status': stat,
            'geni_error': err,
        })
    return retval

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE, TIME_TYPE],
           url_name="openflow_gapi")
def RenewSliver(slice_urn, credentials, expiration_time, **kwargs):
    get_slice(slice_urn)
    return True

@require_creds(True)
@rpcmethod(signature=[SUCCESS_TYPE, URN_TYPE, CREDENTIALS_TYPE],
           url_name="openflow_gapi")
def Shutdown(slice_urn, credentials, **kwargs):
    slice = get_slice(slice_urn)

    client = Client()
    fake_login(client, kwargs["request"].user)
    client.post(reverse("slice_stop", args=[slice.id]))

    return True
