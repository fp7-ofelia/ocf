#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
"""
Graphical user interface functionalities for the
BOWL Aggregate Manager.

@date: Jul 08, 2013
@author: Theresa Enghardt <theresa@inet.tu-berlin.de>
"""

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.slice.models import Slice
from expedient.common.messaging.models import DatedMessage
from expedient.common.utils.plugins.plugincommunicator import *
from expedient.common.utils.plugins.resources.link import Link
from expedient.common.utils.plugins.resources.node import Node
from expedient.common.utils.views import generic_crud

from bowl_plugin.controller.resource import BowlResource as BowlResourceController
from bowl_plugin.forms.BowlResource import BowlResource as BowlResourceModelForm
from bowl_plugin.models import BowlResource as BowlResourceModel,\
    BowlResourceAggregate as BowlResourceAggregateModel

import copy
import logging
import xmlrpclib
import jsonrpclib

def create_resource(request, slice_id, agg_id):
    """Show a page that allows user to add a BOWL Node to the aggregate."""

    logger = logging.getLogger(__name__)
    logger.info("Called %s create_resource with slice_id %s agg_id %s" % (str(request.method), str(slice_id), str(agg_id)))
    if request.method == "POST":
        # Shows error message when aggregate unreachable, disable BOWL node creation and get back to slice detail page
        agg = Aggregate.objects.get(id = agg_id)
        if agg.check_status() == False:
            DatedMessage.objects.post_message_to_user(
                "BOWL Aggregate '%s' is not available" % agg.name,
                request.user, msg_type=DatedMessage.TYPE_ERROR,)
            return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

        if 'create_resource' in request.POST:
            return HttpResponseRedirect(reverse("bowl_plugin_resource_crud", args=[slice_id, agg_id]))
        else:
            return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

def resource_crud(request, slice_id, agg_id, resource_id = None):
    """
    Show a page that allows user to create/edit BOWL Nodes to the Aggregate.
    """
    logger = logging.getLogger(__name__)
    logger.error("Called %s resource_crud with slice_id %s agg_id %s resource_id" % (str(request.method), str(slice_id), str(agg_id), str(resource_id)))
    slice = get_object_or_404(Slice, id = slice_id)
    aggregate = Aggregate.objects.get(id = agg_id)
    error_crud = ""

    def pre_save(instance, created):
        """
        Fills BOWL Node instance prior to its saving.
        Used within the scope of the generic_crud method.
        """
        instance = BowlResourceController.fill(instance, slice, agg_id, resource_id)

    try:
        return generic_crud(request, obj_id=resource_id, model=BowlResourceModel,
                 form_class=BowlResourceModelForm,
                 template="bowl_plugin_resource_crud.html",
                 redirect=lambda inst: reverse("slice_detail", args=[slice_id]),
                 extra_context={"agg": aggregate, "slice": slice, "exception": error_crud, "breadcrumbs": (
                 ("Home", reverse("home")),
                 ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                 ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                 ("%s Bowl Node" % "Update" if resource_id else "Create", reverse("bowl_plugin_resource_crud", args=[slice_id, agg_id])),)
                 }, extra_form_params={}, template_object_name="object", pre_save=pre_save,
                 post_save=None, success_msg=None)
    except ValidationError as e:
        # Django exception message handling is different to Python's...
        error_crud = ";".join(e.messages)
    except Exception as e:
        logger.error("[WARNING] Could not create resource in plugin 'bowl_plugin'. Details: %s" % str(e))
        DatedMessage.objects.post_message_to_user(
            "BOWL Node might have been created, but some problem ocurred: %s" % str(e),
            request.user, msg_type=DatedMessage.TYPE_ERROR)
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))

def manage_resource(request, resource_id, action_type):
    """
    Manages the actions executed over BOWL nodes.
    """
    if action_type == "delete":
        BowlResourceController.delete(resource_id)
    # Go to manage resources again
    return HttpResponse("")

###
# Topology to show in the Expedient
#

def get_bowl_list(slice):
    return BowlResourceModel.objects.filter(slice_id = slice.uuid)

def get_bowl_aggregates(slice):
    bowl_aggs = []
    try:
        bowl_aggs = slice.aggregates.filter(leaf_name=BowlResourceAggregateModel.__name__.lower())
    except:
        pass
    return bowl_aggs

def get_node_description(node):
    description = "<strong>Bowl Node: " + node.name + "</strong><br/><br/>"
    connections = ""
    node_connections = node.get_connections()
    for i, connection in enumerate(node_connections):
        connections += connection.name
        if i < len(node_connections)-1:
            connections += ", "
    description += "<br/>&#149; Connected to: %s" % str(connections)
    return description

def get_aggregate_nodes(slice):
    nodes = []
    bowl_aggs = get_bowl_aggregates(slice)

    for i, bowl_agg in enumerate(bowl_aggs):
        bowl_agg = bowl_agg.bowlresourceaggregate
        nodes = bowl_agg.get_resources()
    return nodes

def get_slice_nodes(slice, chosen_group=None):
    logger = logging.getLogger(__name__)
    nodes = []
    links = []
    bowl_aggs = get_bowl_aggregates(slice)
    logger.debug("BOWL aggregates: %s" % str(bowl_aggs))

    # Getting image for the nodes
    # FIXME: avoid to ask the user for the complete name of the method here! he should NOT know it
    try:
        image_url = reverse('img_media_bowl_plugin', args=("access-point.png",))
    except:
        image_url = 'access-poing.png'

    # For every Bowl AM
    for i, bowl_agg in enumerate(bowl_aggs):
        bowl_agg = bowl_agg.bowlresourceaggregate
        # Iterates over every Bowl Node contained within the slice
        #print "For agg %s" % str(bowl_agg)
        try:
            s = jsonrpclib.Server(bowl_agg.client.url)
            bowl_agg.available = True
            logger.debug("List resources of slice %s" % str(slice.id))
            res = s.ListResources(available=False, slice_urn=str(slice.id))
            for r in res:
#            r = r.bowlresource
            #print "r = %s" % str(r)
                nodes.append(Node(
                # Users shall not be left the choice to choose group/island; otherwise collision may arise
                #name = r.hostname, value = r.id, aggregate = r.aggregate, type = "BOWL Node",
                #description = get_node_description(r), image = image_url)
                    name = r['hostname'], value = r['id'], aggregate = bowl_agg, type = "BOWL Node",
                    description = "Node with DP ID:" + r['default_mac'] + " and IP:"+ r['default_ip'], image = image_url)
                )
#            for connection in r.get_connections():
#                # Two-ways link
#                links.append(
#                    Link(
#                        target = str(r.id), source = str(connection.id),
#                        value = "rsc_d_%s-rsc_id_%s" % (connection.id, r.id)
#                        ),
#                )
#                links.append(
#                    Link(
#                        target = str(r.id), source = str(connection.id),
#                        value = "rsc_d_%s-rsc_id_%s" % (r.id, connection.id)
#                        ),
#                )
        except Exception, e:
            print "Error: %s" % e
    return [nodes, links]

#from expedient.common.utils.plugins.plugininterface imprt PluginInterface
#
#class Plugin(PluginInterface):
#    @staticmethod
def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    logger = logging.getLogger(__name__)
    #logger.error("Called get_ui_data on slice %s" % (str(slice)))
    try:
        #ui_context['bowl_list'] = get_bowl_list(slice)
        ui_context['bowl_aggs'] = get_bowl_aggregates(slice)
        ui_context['bowl_nodes'] = get_aggregate_nodes(slice)
        ui_context['nodes'], ui_context['links'] = get_slice_nodes(slice)
    except Exception as e:
        logger.error("[ERROR] Problem loading UI data for plugin 'bowl_plugin'. Details: %s" % str(e))
    return ui_context

