'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.slice.models import Slice
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch,\
    OpenFlowInterface, OpenFlowInterfaceSliver
from django.http import HttpResponseRedirect
from expedient.common.messaging.models import DatedMessage
from django.forms.models import inlineformset_factory

def home(request, slice_id):
    slice = get_object_or_404(Slice, id=slice_id)
    if request.method == "POST":
        iface_ids = map(int, request.POST.getlist("selected_ifaces"))
        ifaces = OpenFlowInterface.objects.get(id__in=iface_ids)
        # TODO: Send message if id not found.
        # get or create slivers for the ifaces in the slice.
        for iface in ifaces:
            sliver, created = OpenFlowInterfaceSliver.objects.get_or_create(
                slice=slice, resource=iface)
            if created:
                DatedMessage.objects.post_message_to_user(
                    "Successfully added interface %s to slice %s" % (
                        iface, slice.name),
                    request.user, type=DatedMessage.TYPE_SUCCESS)
                
        return HttpResponseRedirect(reverse("html_plugin_flowspace",
                                            args=[slice_id]))
    else:
        return simple.direct_to_template(
            request,
            template="html/select_resources.html",
            extra_context={
                "openflow_aggs": OpenFlowAggregate.objects.filter(
                    slice=slice,
                ),
                "ofswitch_class": OpenFlowSwitch,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
                )
            },
        )
        
def flowspace(request, slice_id):
    """
    Add flowspace.
    """
    slice = get_object_or_404(Slice, id=slice_id)
    
    slivers = OpenFlowInterfaceSliver.objects.filter(slice=slice)
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, SliceFlowSpace)
    
    if request.method == "POST":
        formset = FSFormSet(request.POST, instance=slice)
        if formset.is_valid():
            formset = formset.save()
            DatedMessage.objects.post_message_to_user(
                "Successfully set flowspace for slice %s" % slice.name,
                request.user, type=DatedMessage.TYPE_SUCCESS,
            )
            return HttpResponseRedirect(
                reverse("slice_detail", args=[slice_id]))
    elif request.method == "GET":
        formset = FSFormSet(instance=slice)
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    return simple.direct_to_template(
        request,
        template="html/select_flowspace.html",
        extra_context={
            "slice": slice,
            "fsformset": formset,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
                ("HTML UI - Choose Flowspace", reverse("html_plugin_flowspace", args=[slice_id])),
            ),
        },
    )
