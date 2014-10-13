'''
Created on Apr 20, 2010

@author: jnaous
'''
import rspec as rspec_mod
from openflow.plugin.models import \
    OpenFlowSliceInfo, OpenFlowInterfaceSliver,\
    FlowSpaceRule
import logging
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.utils import create_or_update
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.users.models import UserProfile
from expedient.clearinghouse.geni.models import GENISliceInfo
from expedient.clearinghouse.project.views import create_project_roles
from expedient.common.middleware import threadlocals
from django.db.utils import IntegrityError
from datetime import datetime, timedelta
from django.conf import settings
import dateutil

logger = logging.getLogger("openflow.plugin.gapi.gapi")

class OpenFlowGAPIException(Exception):
    pass

class DuplicateSliceNameException(OpenFlowGAPIException):
    def __init__(self, slice_name):
        self.slice_name = slice_name
        super(DuplicateSliceNameException, self).__init__(
            "Slice name '%s' is already associated with a different project."
            % slice_name
        )

def get_slice(slice_urn):
    # get the slice
    slice = Slice.objects.get(geni_slice_info__slice_urn=slice_urn)
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
    (project_name, project_desc, slice_name, slice_desc, slice_expiry,
    controller_url, firstname, lastname, affiliation,
    email, password, slivers) = rspec_mod.parse_slice(rspec)

    logger.debug("Parsed Rspec")
    
    slice_expiry = datetime.fromtimestamp(slice_expiry)

    give_permission_to("can_create_project", Project, user)

    user.first_name = firstname
    user.last_name = lastname
    user.email = email
    profile = UserProfile.get_or_create_profile(user)
    profile.affiliation = affiliation
    user.save()
    profile.save()
    
    # Check if the slice exists
    try:
        slice = get_slice(slice_urn)
        # update the slice info
        slice.description = slice_desc
        slice.name = slice_name
        slice.expiration_date = slice_expiry
        slice.save()
        # update the project info
        slice.project.name = project_name
        slice.project.description = project_desc
        slice.project.save()
        project = slice.project
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
            project = Project.objects.create(
                name=project_name,
                description=project_desc,
            )
            create_project_roles(project, user)
        
        # create the slice
        logger.debug("Creating slice")
        
        try:
            slice = Slice.objects.create(
                name=slice_name,
                description=slice_desc,
                project=project,
                owner=user,
                expiration_date = slice_expiry,
            )
        except IntegrityError:
            raise DuplicateSliceNameException(slice_name)

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
    create_or_update(
        GENISliceInfo,
        filter_attrs={
            "slice": slice,
        },
        new_attrs={
            "slice_urn": slice_urn,
        },
    )
    
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
        logger.debug("Creating flowspace %s" % fs_dict)
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
    tl = threadlocals.get_thread_locals()
    tl["project"] = project
    tl["slice"] = slice
    slice.start(user)
    logger.debug("Done creating sliver")

    return rspec_mod.create_resv_rspec(user, slice)

def DeleteSliver(slice_urn, user):
    slice = get_slice(slice_urn)
    project = slice.project
    tl = threadlocals.get_thread_locals()
    tl["project"] = project
    tl["slice"] = slice
    slice.stop(user)
    slice.delete()
    # delete the project if there are no more slices in it
    if Slice.objects.filter(project=project).count() == 0:
        project.delete()
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
    slice = get_slice(slice_urn)
    new_expiration_date = dateutil.parser.parse(str(expiration_time))
    slice.expiration_date = new_expiration_date
    slice.save()
    return True

def Shutdown(slice_urn, user):
    slice = get_slice(slice_urn)
    tl = threadlocals.get_thread_locals()
    tl["project"] = slice.project
    tl["slice"] = slice
    slice.stop(user)
    return True
