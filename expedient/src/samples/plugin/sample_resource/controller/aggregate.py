"""
Controller for the SampleResource aggregate.
Performs aggregate CRUD operations and the
synchronization with the resources it contains.

@date: Jun 12, 2013
@author: CarolinaFernandez
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
from sample_resource.controller.resource import SampleResource as SampleResourceController
from sample_resource.forms.SampleResourceAggregate import SampleResourceAggregate as SampleResourceAggregateForm
from sample_resource.forms.xmlrpcServerProxy import xmlrpcServerProxy as xmlrpcServerProxyForm
from sample_resource.models.SampleResourceAggregate import SampleResourceAggregate as SampleResourceAggregateModel
from sample_resource.models.SampleResource import SampleResource as SampleResourceModel
import xmlrpclib

class am_resource(object):
    """
    Used to extend any object properties.
    """
    pass

def aggregate_crud(request, agg_id=None):
    '''
    Create/update a SampleResource Aggregate.
    '''
    if agg_id != None:
        aggregate = get_object_or_404(SampleResourceAggregateModel, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None

    extra_context_dict = {}
    errors = ""

    if request.method == "GET":
        agg_form = SampleResourceAggregateForm(instance=aggregate)
        client_form = xmlrpcServerProxyForm(instance=client)
        
    elif request.method == "POST":
        agg_form = SampleResourceAggregateForm(
            data=request.POST, instance=aggregate)
        client_form = xmlrpcServerProxyForm(
            data=request.POST, instance=client)

        if client_form.is_valid() and agg_form.is_valid():
            # Ping is tried after every field check
            client = client_form.save(commit=False)
            s = xmlrpclib.Server('https://'+client.username+':'+client.password+'@'+client.url[8:])
            try:
                s.ping('ping')
            except:
                errors = "Could not connect to server: username, password or url are not correct"
                DatedMessage.objects.post_message_to_user(
                    errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,
                )
                extra_context_dict['errors'] = errors

            if not errors:
                client = client_form.save()
                aggregate = agg_form.save(commit=False)
                aggregate.client = client
                aggregate.save()
                agg_form.save_m2m()
                aggregate.save()
                # Update agg_id to sync its resources
                agg_id = aggregate.pk
                # Get resources from SampleResource AM's xmlrpc server every time the AM is updated
                try:
                    do_sync = True
                    if agg_form.is_bound:
                        do_sync = agg_form.data.get("sync_resources")
                    else:
                        do_sync = agg_form.initial.get("sync_resources")

                    if do_sync:
                        failed_resources = sync_am_resources(agg_id, s)

                        if failed_resources:
                            DatedMessage.objects.post_message_to_user(
                                "Could not synchronize resources %s within Expedient" % str(failed_resources),
                                user=request.user, msg_type=DatedMessage.TYPE_WARNING,
                            )
                except:
                    warning = "Could not synchronize AM resources within Expedient"
                    DatedMessage.objects.post_message_to_user(
                        errors, user=request.user, msg_type=DatedMessage.TYPE_WARNING,
                    )
                    extra_context_dict['errors'] = warning

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
        extra_context_dict['available'] = aggregate.check_status() if agg_id else False

    # Updates the dictionary with the common fields
    extra_context_dict.update({
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("%s SampleResource Aggregate" % ("Update" if agg_id else "Create"),
                 request.path),
            )
        })

    return simple.direct_to_template(
        request,
        template="sample_resource_aggregate_crud.html",
        extra_context=extra_context_dict
    )

def delete_resources(agg_id):
    resource_set = SampleResourceAggregateModel.objects.get(id = agg_id).resource_set.all()
    for resource in resource_set:
        resource.delete()

def sync_am_resources(agg_id, xmlrpc_server):
    """
    Retrieves SampleResource objects from the AM's xmlrpc server every time the AM is updated
    """
    connections = dict()
    failed_resources = []
    resources = xmlrpc_server.get_resources()
    context = etree.iterparse(BytesIO(resources))
    delete_resources(agg_id)
    aggregate = SampleResourceAggregateModel.objects.get(id = agg_id)
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
                SampleResourceController.create(instance, agg_id)
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
                    res = SampleResourceModel.objects.get(name = connection)
                    if res:
                        connections_aux.append(res)
                except:
                   pass
            connections[node] = connections_aux
            # Setting connections on resource with name as in 'node' var
            node_resource = SampleResourceModel.objects.get(name = node)
            node_resource.set_connections(connections[node])
            node_resource.save()
    except:
        pass

    return failed_resources

