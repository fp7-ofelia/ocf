"""
Graphical user interface functionalities for the
GeniApi Aggregate Manager.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from modules.aggregate.models import Aggregate
from modules.slice.models import Slice
from common.messaging.models import DatedMessage
from common.utils.plugins.plugincommunicator import *
from common.utils.plugins.resources.link import Link
from common.utils.plugins.resources.node import Node
from common.utils.views import generic_crud
from geni_api.controller.resource import GeniApi as GeniApiController
from geni_api.forms.GeniApi import GeniApi as GeniApiModelForm
from geni_api.models import GeniApi as GeniApiModel,\
    GeniApiAggregate as GeniApiAggregateModel

import copy
import logging
import xmlrpclib

def create_resource(request, slice_id, agg_id):
    """Show a page that allows user to add a GeniApi to the aggregate."""

    if request.method == "POST":
        # Shows error message when aggregate unreachable, disable GeniApi creation and get back to slice detail page
        agg = Aggregate.objects.get(id = agg_id)
        if agg.check_status() == False:
            DatedMessage.objects.post_message_to_user(
                "GeniApi Aggregate '%s' is not available" % agg.name,
                request.user, msg_type=DatedMessage.TYPE_ERROR,)
            return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

        if 'create_resource' in request.POST:
            return HttpResponseRedirect(reverse("geni_api_resource_crud", args=[slice_id, agg_id]))
        else:
            return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

def resource_crud(request, slice_id, agg_id, resource_id = None):
    """
    Show a page that allows user to create/edit GeniApi's to the Aggregate.
    """
    slice = get_object_or_404(Slice, id = slice_id)
    aggregate = Aggregate.objects.get(id = agg_id)
    error_crud = ""

    def pre_save(instance, created):
        """
        Fills GeniApi instance prior to its saving.
        Used within the scope of the generic_crud method.
        """
        instance = GeniApiController.fill(instance, slice, agg_id, resource_id)

    try:
        return generic_crud(request, obj_id=resource_id, model=GeniApiModel,
                 form_class=GeniApiModelForm,
                 template="geni_api_resource_crud.html",
                 redirect=lambda inst: reverse("slice_detail", args=[slice_id]),
                 extra_context={"agg": aggregate, "slice": slice, "exception": error_crud, "agg_form": GeniApiModelForm,"breadcrumbs": (
                 ("Home", reverse("home")),
                 ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                 ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                 ("%s GeniApi" % "Update" if resource_id else "Create", reverse("geni_api_resource_crud", args=[slice_id, agg_id])),)
                 }, extra_form_params={}, template_object_name="object", pre_save=pre_save,
                 post_save=None, success_msg=None)
    except ValidationError as e:
        # Django exception message handling is different to Python's...
        error_crud = ";".join(e.messages)
    except Exception as e:
        print "[WARNING] Could not create resource in plugin 'geni_api'. Details: %s" % str(e)
        DatedMessage.objects.post_message_to_user(
            "GeniApi might have been created, but some problem ocurred: %s" % str(e),
            request.user, msg_type=DatedMessage.TYPE_ERROR)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

def manage_resource(request, resource_id, action_type):
    """
    Manages the actions executed over GeniApi's.
    """
    if action_type == "delete":
        GeniApiController.delete(resource_id)
    # Go to manage resources again
    return HttpResponse("")

###
# Topology to show in the Expedient
#

def get_sr_list(slice):
    return GeniApiModel.objects.filter(slice_id = slice.uuid)

def get_sr_aggregates(slice):
    sr_aggs = []
    try:
        sr_aggs = slice.aggregates.filter(leaf_name=GeniApiAggregateModel.__name__.lower())
    except:
        pass
    return sr_aggs

def get_node_description(node):
    description = "<strong>Sample Resource: " + node.name + "</strong><br/><br/>"
    description += "&#149; Temperature: %s (&#176;%s)" % (str(node.get_temperature()), str(node.get_temperature_scale()))
    connections = ""
    node_connections = node.get_connections()
    for i, connection in enumerate(node_connections):
        connections += connection.name
        if i < len(node_connections)-1:
            connections += ", "
    description += "<br/>&#149; Connected to: %s" % str(connections)
    return description

def get_nodes_links(slice, chosen_group=None):
    nodes = []
    links = []
    sr_aggs = get_sr_aggregates(slice)

    # Getting image for the nodes
    # FIXME: avoid to ask the user for the complete name of the method here! he should NOT know it
    try:
        image_url = reverse('img_media_geni_api', args=("sensor-tiny.png",))
    except:
        image_url = 'sensor-tiny.png'

    # For every GeniApi AM
    for i, sr_agg in enumerate(sr_aggs):
        sr_agg = sr_agg.sampleresourceaggregate
        # Iterates over every GeniApi contained within the slice
        for sr in sr_agg.get_resources():
            sr = sr.sampleresource
            nodes.append(Node(
                # Users shall not be left the choice to choose group/island; otherwise collision may arise
                name = sr.name, value = sr.id, aggregate = sr.aggregate, type = "Sample resource",
                description = get_node_description(sr), image = image_url)
            )
            for connection in sr.get_connections():
                # Two-ways link
                links.append(
                    Link(
                        target = str(sr.id), source = str(connection.id),
                        value = "rsc_id_%s-rsc_id_%s" % (connection.id, sr.id)
                        ),
                )
                links.append(
                    Link(
                        target = str(sr.id), source = str(connection.id),
                        value = "rsc_id_%s-rsc_id_%s" % (sr.id, connection.id)
                        ),
                )
    return [nodes, links]

#from common.utils.plugins.plugininterface import PluginInterface
#
#class Plugin(PluginInterface):
#    @staticmethod
def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    try:
        ui_context['sr_list'] = get_sr_list(slice)
        ui_context['sr_aggs'] = get_sr_aggregates(slice)
        ui_context['nodes'], ui_context['links'] = get_nodes_links(slice)
    except Exception as e:
        print "[ERROR] Problem loading UI data for plugin 'geni_api'. Details: %s" % str(e)
    return ui_context

