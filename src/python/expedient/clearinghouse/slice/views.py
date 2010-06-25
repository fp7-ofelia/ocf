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

logger = logging.getLogger("SliceViews")

TEMPLATE_PATH = "expedient/clearinghouse/slice"

def create(request, proj_id):
    '''Create a slice'''
    project = get_object_or_404(Project, id=proj_id)
    
    def pre_save(instance, created):
        instance.project = project
        instance.owner = request.user
        instance.reserved = False
    
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
        success_msg = lambda instance: "Successfully created slice %s." % instance.name,
    )

def update(request, slice_id):
    '''Update a slice's information'''
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
    req = create_update.delete_object(
        request,
        model=Slice,
        post_delete_redirect=reverse('project_detail', args=[project.id]),
        object_id=slice_id,
        template_name=TEMPLATE_PATH+"/confirm_delete.html",
    )
    if req.status_code == HttpResponseRedirect.status_code:
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted slice %s" % slice.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    return req

def detail(request, slice_id):
    '''Show information about the slice'''
    slice = get_object_or_404(Slice, id=slice_id)
    return list_detail.object_detail(
        request,
        Slice.objects.all(),
        object_id=slice_id,
        template_name=TEMPLATE_PATH+"/detail.html",
        template_object_name="slice",
        extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
            ),
        }
    )
    
def start(request, slice_id):
    '''Start the slice on POST'''
    slice = get_object_or_404(Slice, id=slice_id)
    if request.method == "POST":
        slice.start(request.user)
        DatedMessage.objects.post_message_to_user(
            "Successfully started slice %s" % slice.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))
    
def stop(request, slice_id):
    '''Stop the slice on POST'''
    slice = get_object_or_404(Slice, id=slice_id)
    if request.method == "POST":
        slice.stop(request.user)
        DatedMessage.objects.post_message_to_user(
            "Successfully stopped slice %s" % slice.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

def select_ui_plugin(request, slice_id):
    slice = get_object_or_404(Slice, id=slice_id)
    
    plugins_info = getattr(settings, "UI_PLUGINS", [])
    
    logger.debug("select_ui_plugin plugins_info %s" % plugins_info)
    
    # plugin functions should return (name, description, url)
    plugins = [get_callable(plugin[0])(slice) for plugin in plugins_info]

    logger.debug("select_ui_plugin plugins %s" % plugins)
    
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

# TODO: The below functions are pretty much the same as the ones in
# project.views. We should merge them.
def add_aggregate(request, slice_id):
    '''Add aggregate to slice'''
    
    slice = get_object_or_404(Slice, id=slice_id)
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
        items = request.POST.items()
        agg_id = -1
        for i in items:
            if i[1] == "Select":
                try:
                    agg_id = int(i[0]) # there should be only one item
                except:
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
    # TODO: This function might actually change the DB. So change to post
    slice = get_object_or_404(Slice, id=slice_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=slice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()
    return HttpResponseRedirect(aggregate.add_to_slice(
        slice, reverse("slice_detail", args=[slice_id])))

def remove_aggregate(request, slice_id, agg_id):
    # TODO: This function might actually change the DB. So change to post
    slice = get_object_or_404(Slice, id=slice_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=slice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()
    return HttpResponseRedirect(aggregate.remove_from_slice(
        slice, reverse("slice_detail", args=[slice_id])))
