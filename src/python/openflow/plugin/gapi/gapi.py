'''
Created on Apr 20, 2010

@author: jnaous
'''
import rspec as rspec_mod
from openflow.plugin.models import \
    OpenFlowSliceInfo, OpenFlowInterfaceSliver,\
    FlowSpaceRule
import logging
from django.test import Client
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.project.models import Project
from django.core.urlresolvers import reverse
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.utils import create_or_update
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.users.models import UserProfile
from expedient_geni.models import GENISliceInfo

logger = logging.getLogger("openflow.plugin.gapi.gapi")

def get_slice(slice_urn):
    # get the slice
    slice = Slice.objects.get(gapislice__slice_urn=slice_urn)
    return slice
    
def GetVersion():
    return dict(geni_api=1)

def ListResources(options, user):
    import base64, zlib

    if not options:
        options = dict()
        
    slice_urn = options.pop('geni_slice_urn', None)
    geni_available = options.pop('geni_available', True)

    if slice_urn:
        slice = get_slice(slice_urn)
        result = rspec_mod.create_resv_rspec(user, slice)
    else:
        result = rspec_mod.get_resources(slice_urn, geni_available)

    # Optionally compress the result
    if 'geni_compressed' in options and options['geni_compressed']:
        logger.debug("Compressing rspec")
        result = base64.b64encode(zlib.compress(result))

    return result

def CreateSliver(slice_urn, rspec, user):

    (project_name, project_desc, slice_name, slice_desc, 
    controller_url, firstname, lastname, affiliation,
    email, password, slivers) = rspec_mod.parse_slice(rspec)

    logger.debug("Parsed Rspec")

    give_permission_to("can_create_project", Project, user)

    client = Client()
    fake_login(client, user)
    
    user.firstname = firstname
    user.lastname = lastname
    profile = UserProfile.get_or_create_profile(user)
    profile.affiliation = affiliation
    user.save()
    profile.save()
    
    # Check if the slice exists
    try:
        slice = Slice.objects.get(gapislice__slice_urn=slice_urn)
        # update the slice info
        slice.description = slice_desc
        slice.name = slice_name
        slice.save()
        # update the project info
        slice.project.name = project_name
        slice.project.description = project_desc
        slice.project.save()
    except Slice.DoesNotExist:
        # Check if the project exists
        try:
            project = Project.objects.get(name=project_name)
            # update the project info
            logger.debug("Updating project")
            project.description = project_desc
            project.save()
        except Project.DoesNotExist:
            # create the project
            logger.debug("Creating project")
            test_get_and_post_form(
                client, url=reverse("project_create"),
                params={"name": project_name, "description": project_desc}
            )
            project = Project.objects.get(name=project_name)
        
        # create the slice
        logger.debug("Creating slice")
        test_get_and_post_form(
            client, url=reverse("slice_create", args=[project.id]),
            params={"name": slice_name, "description": slice_desc}
        )
        slice = Slice.objects.get(gapislice__slice_urn=slice_urn)

    logger.debug("Creating/updating slice info")
    
    # create openflow slice info for the slice
    create_or_update(
        OpenFlowSliceInfo,
        filter_attrs={"slice": slice},
        new_attrs={
            "controller_url": controller_url,
            "password": password,
            "email": email,
        },
    )
    
    logger.debug("creating gapislice")

    # store a pointer to this slice using the slice_urn
    GENISliceInfo.objects.get_or_create(slice_urn=slice_urn, slice=slice)
    
    logger.debug("adding resources")

    sliver_ids = []
    
    # delete all flowspace in the slice
    FlowSpaceRule.objects.filter(slivers__slice=slice).delete()
    
    # add the new flowspace
    for fs_dict, iface_qs in slivers:
        # give the user, project, slice permission to use the aggregate
        aggregate_ids = list(iface_qs.values_list("aggregate", flat=True))
        for agg_id in aggregate_ids:
            aggregate = Aggregate.objects.get(id=agg_id).as_leaf_class()
            give_permission_to("can_use_aggregate", aggregate, user)
            give_permission_to("can_use_aggregate", aggregate, project)
            give_permission_to("can_use_aggregate", aggregate, slice)

        # Create flowspace
        fs = FlowSpaceRule.objects.create(**fs_dict)

        # make sure all the selected interfaces are added
        for iface in iface_qs:
            sliver, _ = OpenFlowInterfaceSliver.objects.get_or_create(
                slice=slice, resource=iface)
            sliver_ids.append(sliver.id)
            fs.slivers.add(sliver)
        
    logger.debug("Deleting old resources")

    # Delete all removed interfaces
    OpenFlowInterfaceSliver.objects.exclude(id__in=sliver_ids).delete()
        
    logger.debug("Starting the slice %s %s" % (slice, slice.name))
    
    # make the reservation
    client.post(reverse("slice_start", args=[slice.id]))
    
    logger.debug("Done creating sliver")

    client.logout()

    return rspec_mod.create_resv_rspec(user, slice)

def DeleteSliver(slice_urn, user):
    slice = get_slice(slice_urn)
    project = slice.project
    client = Client()
    fake_login(client, user)
    client.post(reverse("slice_delete", args=[slice.id]))
    # delete the project if there are no more slices in it
    if Slice.objects.filter(project=project).count() == 0:
        client.post(reverse("project_delete", args=[project.id]))
    return True

def SliverStatus(slice_urn):
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

def RenewSliver(slice_urn, expiration_time):
    get_slice(slice_urn)
    return True

def Shutdown(slice_urn, user):
    slice = get_slice(slice_urn)

    client = Client()
    fake_login(client, user)
    client.post(reverse("slice_stop", args=[slice.id]))

    return True
