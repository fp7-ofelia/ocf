'''
Created on Jun 17, 2010

@author: jnaous
'''
from django.views.generic import create_update, list_detail, simple
from django.core.urlresolvers import reverse, get_callable
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.aggregate.models import Aggregate
from models import Slice
from forms import SliceCrudForm
from django.conf import settings
import logging
from expedient.common.permissions.shortcuts import must_have_permission, give_permission_to
from vt_plugin.models import VM
logger = logging.getLogger("SliceViews")
import uuid
from  expedient.clearinghouse.slice.utils import parseFVexception

TEMPLATE_PATH = "expedient/clearinghouse/slice"

def create(request, proj_id):
    '''Create a slice'''
    project = get_object_or_404(Project, id=proj_id)
    
    must_have_permission(request.user, project, "can_create_slices")
    
    def pre_save(instance, created):
        instance.project = project
        instance.owner = request.user
	#Generate UUID: fixes caching problem on model default value
	instance.uuid = uuid.uuid4()
	instance.save()
        
        instance.reserved = False
    
    #use to give the can_delete_slices over the slice to the creator and the owners of the project 
    def post_save(instance, created):
	give_permission_to("can_delete_slices", instance, instance.owner, giver=None, can_delegate=False)
#	for projectOwner in instance.project._get_owners():
#		give_permission_to("can_delete_slices", instance, projectOwner, giver=None, can_delegate=False)	

 
    return generic_crud(
        request, None, Slice,
        TEMPLATE_PATH+"/create_update.html",
        redirect=lambda instance:reverse("slice_detail", args=[instance.id]),
        form_class=SliceCrudForm,
        extra_context={
            "project": project,
            "title": "Create slice",
            "cancel_url": reverse("project_detail", args=[proj_id]),
        },
        pre_save=pre_save,
        post_save=post_save,
        success_msg = lambda instance: "Successfully created slice %s." % instance.name,
    )

def update(request, slice_id):
    '''Update a slice's information'''
    
    project = get_object_or_404(Project, slice__pk=slice_id)
    must_have_permission(request.user, project, "can_edit_slices")

    return generic_crud(
        request, slice_id, Slice,
        TEMPLATE_PATH+"/create_update.html",
        redirect=lambda instance:reverse("slice_detail", args=[instance.id]),
        extra_context={
            "title": "Create slice",
            "cancel_url": reverse("slice_detail", args=[slice_id]),
        },
        form_class=SliceCrudForm,
        success_msg = lambda instance: "Successfully updated slice %s." % instance.name,
    )

def delete(request, slice_id):
    '''Delete the slice'''
    slice = get_object_or_404(Slice, id=slice_id)
    project = slice.project
    
    #Slice can edited and used by anyone in the project, but only the owner of the slice
    #or the project's owner can delete it
    try:
        must_have_permission(request.user, slice, "can_delete_slices")
    except Exception,e:
        try:
            must_have_permission(request.user, project, "can_delete_slices")
        except Exception,e2:
            raise e if e else e2

    if request.method == "POST":
        stop(request, slice_id)
        slice.delete()
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted slice %s" % slice.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(
            reverse('project_detail', args=[project.id]))

    else:
        from vt_plugin.models.VM import VM
        if VM.objects.filter(sliceId = slice.uuid):
            DatedMessage.objects.post_message_to_user(
            "Please before deleting the slice %s, delete all the VMs in it" % slice.name,
            request.user, msg_type=DatedMessage.TYPE_ERROR)
            return detail(request, slice_id)
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/confirm_delete.html",
            extra_context={"object": slice},
        )

def detail(request, slice_id):
    '''Show information about the slice'''
    slice = get_object_or_404(Slice, id=slice_id)

    must_have_permission(request.user, slice.project, "can_view_project")
    
    resource_list = [rsc.as_leaf_class() for rsc in slice.resource_set.all()]
    vms_list = VM.objects.filter(sliceId = slice.uuid)
    from openflow.plugin.models import OpenFlowSliceInfo
    try:
        controller_url = OpenFlowSliceInfo.objects.get(slice=slice).controller_url
    except:
        controller_url= "Not set"
    extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
            ),
            "resource_list": resource_list,
            "vms_list": vms_list,
	    "controller_url":controller_url 
    }
    from expedient.ui.html.views import getUIdata
    #extra_context+=getUIdata(request,slice)
    
    return list_detail.object_detail(
        request,
        Slice.objects.all(),
        object_id=slice_id,
        template_name=TEMPLATE_PATH+"/detail.html",
        template_object_name="slice",
	extra_context=dict(extra_context.items()+getUIdata(request,slice).items())
    )
    
def start(request, slice_id):
    '''Start the slice on POST'''
    slice = get_object_or_404(Slice, id=slice_id)
    
    must_have_permission(request.user, slice.project, "can_start_slices")
    
    if request.method == "POST":
        try:
            slice.start(request.user)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print e
            DatedMessage.objects.post_message_to_user(
                "Error starting slice %s: %s" % (
                    slice.name, parseFVexception(e)),
                user=request.user, msg_type=DatedMessage.TYPE_ERROR)
        else:
            DatedMessage.objects.post_message_to_user(
                "Successfully started slice %s" % slice.name,
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))
    else:
        return HttpResponseNotAllowed(["POST"])
    
def stop(request, slice_id):
    '''Stop the slice on POST'''
    slice = get_object_or_404(Slice, id=slice_id)
    
    must_have_permission(request.user, slice.project, "can_stop_slices")
    
    if request.method == "POST":
        try:
            slice.stop(request.user)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print e
            DatedMessage.objects.post_message_to_user(
                "Error stopping slice %s: %s" % (
                    slice.name, parseFVexception(e)),
                user=request.user, msg_type=DatedMessage.TYPE_ERROR)
        else:
            DatedMessage.objects.post_message_to_user(
                "Successfully stopped slice %s" % slice.name,
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))
    else:
        return HttpResponseNotAllowed(["POST"])

def select_ui_plugin(request, slice_id):
    slice = get_object_or_404(Slice, id=slice_id)
    
    plugins_info = getattr(settings, "UI_PLUGINS", [])
    
    logger.debug("select_ui_plugin plugins_info %s" % (plugins_info,))
    
    # plugin functions should return (name, description, url)
    plugins = [get_callable(plugin[0])(slice) for plugin in plugins_info]

    logger.debug("select_ui_plugin plugins %s" % (plugins,) )
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/select_ui_plugin.html",
        extra_context={
            "plugins": plugins, "slice": slice,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("Select UI", request.path),
            ),
        },
    )

def add_aggregate(request, slice_id):
    '''Add aggregate to slice'''
    
    slice = get_object_or_404(Slice, id=slice_id)
    
    must_have_permission(request.user, slice.project, "can_edit_slices")
    
    aggregate_list = slice.project.aggregates.exclude(
        id__in=slice.aggregates.values_list("id", flat=True))
    
    if request.method == "GET":
        return simple.direct_to_template(
            request, template=TEMPLATE_PATH+"/add_aggregates.html",
            extra_context={
                "aggregate_list": aggregate_list,
                "slice": slice,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("Add Slice Aggregates", request.path),
                ),
            }
        )
    
    elif request.method == "POST":
        # check which submit button was pressed
        try:
            agg_id = int(request.POST.get("id", 0))
        except ValueError:
            raise Http404

        if agg_id not in aggregate_list.values_list("id", flat=True):
            raise Http404
        aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
        return HttpResponseRedirect(aggregate.add_to_slice(
            slice, reverse("slice_add_agg", args=[slice_id])))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
def update_aggregate(request, slice_id, agg_id):
    '''Update any info stored at the aggregate'''
    
    slice = get_object_or_404(Slice, id=slice_id)

    must_have_permission(request.user, slice.project, "can_edit_slices")
    
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=slice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()

    if request.method == "POST":
        #return HttpResponseRedirect(aggregate.add_to_slice(
        return HttpResponseRedirect(aggregate.add_controller_to_slice(
            slice, reverse("slice_detail", args=[slice_id])))
    else:
        return HttpResponseNotAllowed(["POST"])

def remove_aggregate(request, slice_id, agg_id):

    slice = get_object_or_404(Slice, id=slice_id)

    must_have_permission(request.user, slice.project, "can_edit_slices")
    
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=slice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()
            
    if request.method == "POST":
        return HttpResponseRedirect(aggregate.remove_from_slice(
            slice, reverse("slice_detail", args=[slice_id])))
    else:
        return HttpResponseNotAllowed(["POST"])
