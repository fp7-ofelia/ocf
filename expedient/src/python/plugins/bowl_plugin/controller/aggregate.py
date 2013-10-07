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
Class that communicates with the BOWL AM
Performs aggregate CRUD operations and the
synchronization with the resources it contains.

@date: Jul 08, 2013
@author: Theresa Enghardt
"""

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import simple
from expedient.clearinghouse.utils import post_message_to_current_user
from expedient.common.messaging.models import DatedMessage
from expedient.common.permissions.shortcuts import give_permission_to
from io import BytesIO
from lxml import etree
from bowl_plugin.controller.resource import BowlResource as BowlResourceController
from bowl_plugin.forms.BowlResourceAggregate import BowlResourceAggregate as BowlResourceAggregateForm
from bowl_plugin.forms.xmlrpcServerProxy import xmlrpcServerProxy as xmlrpcServerProxyForm
from bowl_plugin.models.BowlResourceAggregate import BowlResourceAggregate as BowlResourceAggregateModel
from bowl_plugin.models.BowlResource import BowlResource as BowlResourceModel
#import xmlrpclib
import jsonrpclib
import logging

class am_resource(object):
    """
    Used to extend any object properties.
    """
    pass

def aggregate_crud(request, agg_id=None):
    '''
    Create/update a BowlResource Aggregate.
    '''

    logger = logging.getLogger(__name__)
    logger.info("Called %s aggregate_crud with agg_id %s" % (str(request.method), str(agg_id)))
    if agg_id != None:
        aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None

    #if aggregate == None:
    #    logger.error('Beer: Aggregate is None')
    #else:
    #    logger.error("Beer: Aggregate is not None: %s" % str(aggregate))
    extra_context_dict = {}
    errors = ""

    if request.method == "GET":
        agg_form = BowlResourceAggregateForm(instance=aggregate)
        client_form = xmlrpcServerProxyForm(instance=client)
        
    elif request.method == "POST":
        agg_form = BowlResourceAggregateForm(
            data=request.POST, instance=aggregate)
        client_form = xmlrpcServerProxyForm(
            data=request.POST, instance=client)

        if client_form.is_valid() and agg_form.is_valid():
            client = client_form.save(commit=False)
            url = "https://" + client.url[8:]
            logger.debug("Trying to connect to AM %s" % str(url))

            #s = xmlrpclib.Server('https://foo:bar@'+url)
            s = jsonrpclib.Server(url)
            logger.debug("Server: %s" % str(s))
            try:
                res = s.ListResources(False)
                logger.debug("Resources: %s" % str(res))
                #s.ping('ping')
            except Exception, e:
                logger.error("Could not connect: %s" % e)
                errors = "Could not connect to server %s: %s" % (str(url), e)
                DatedMessage.objects.post_message_to_user(
                    errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,
                )
                extra_context_dict['errors'] = errors

            if not errors:
                client = client_form.save()
                aggregate = agg_form.save(commit=False)
                aggregate.client = client
                aggregate.available = True
                aggregate.save()
                agg_form.save_m2m()
                aggregate.save()
                # Update agg_id to sync its resources
                agg_id = aggregate.pk
                give_permission_to(
                   "can_use_aggregate",
                   aggregate,
                   request.user,
                   can_delegate=True
                )
                give_permission_to(
                    "can_edit_aggregate",
                    aggregate,
                    request.user,
                    can_delegate=True
                )
                DatedMessage.objects.post_message_to_user(
                    "Successfully created/updated aggregate %s" % aggregate.name,
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,
                )
                return HttpResponseRedirect("/")
    else:
        return HttpResponseNotAllowed("GET", "POST")


    if not errors:
        extra_context_dict['available'] = True if agg_id else False

    # Updates the dictionary with the common fields
    extra_context_dict.update({
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("%s BowlResource Aggregate" % ("Update" if agg_id else "Create"),
                 request.path),
            )
        })

    return simple.direct_to_template(
        request,
        template="bowl_plugin_aggregate_crud.html",
        extra_context=extra_context_dict
    )

def aggregate_delete(request, agg_id=None):
    '''
    Delete a BowlResource Aggregate.
    '''

    logger = logging.getLogger(__name__)
    logger.info("Called %s aggregate_delete with agg_id %s" % (str(request.method), str(agg_id)))
    if agg_id != None:
        aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None


def delete_resources(agg_id):
    resource_set = BowlResourceAggregateModel.objects.get(id = agg_id).resource_set.all()
    for resource in resource_set:
        resource.delete()

def sync_am_resources(agg_id, xmlrpc_server):
    """
    Retrieves BowlResource objects from the AM's xmlrpc server every time the AM is updated
    """
    connections = dict()
    failed_resources = []
    resources = xmlrpc_server.get_resources()
    context = etree.iterparse(BytesIO(resources))
    delete_resources(agg_id)
    aggregate = BowlResourceAggregateModel.objects.get(id = agg_id)
#    for slice in aggregate.slice_set:
    # File (nodes)
    for action, elem in context:
        node_name = ""
        instance = am_resource()
        children_context = elem.iterchildren()
        # Node (tags)
        for elem in children_context:
            if "connection" not in elem.tag:
                setattr(instance, elem.tag, elem.text)
                if elem.tag == "name":
                    node_name = elem.text
            elif elem.tag == "connections":
                connections[node_name] = []
                connections_context = elem.iterchildren()
                for connection in connections_context:
                    connections[node_name].append(connection.text)
        try:
            if instance:
#                SampleResourceController.create(instance, agg_id, slice)
                BowlResourceController.create(instance, agg_id)
        except:
            try:
                failed_resources.append(instance.name)
            except:
                pass

    # Connections between SampleResources are computed later, when all nodes have been created 
    try:
        for node, node_connections in connections.iteritems():
            connections_aux = []
            for connection in node_connections:
                try:
                    # Linked to another SampleResources
                    res = BowlResourceModel.objects.get(name = connection)
                    if res:
                        connections_aux.append(res)
                except:
                   pass
            connections[node] = connections_aux
            # Setting connections on resource with name as in 'node' var
            node_resource = BowlResourceModel.objects.get(name = node)
            node_resource.set_connections(connections[node])
            node_resource.save()
    except:
        pass

    return failed_resources

