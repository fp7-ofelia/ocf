from django.views.generic import simple, list_detail, date_based, create_update
from clearinghouse.messaging.models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseServerError
from django.core.urlresolvers import reverse
from clearinghouse.openflow.forms import OpenFlowAggregateForm
from clearinghouse.aggregate.models import AggregateAdminInfo
from clearinghouse.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyForm
from clearinghouse.openflow.models import OpenFlowAggregate
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib import auth
import datetime

def aggregate_crud(request, agg_id=None):
    '''
    Create a new OpenFlow Aggregate.
    '''
    
    if agg_id != None:
        aggregate = get_object_or_404(OpenFlowAggregate, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None
        
    if request.method == "GET":
        agg_form = OpenFlowAggregateForm(instance=aggregate)
        client_form = PasswordXMLRPCServerProxyForm(instance=client)
        
    elif request.method == "POST":
        agg_form = OpenFlowAggregateForm(request.POST, instance=aggregate)
        client_form = PasswordXMLRPCServerProxyForm(request.POST, instance=client)
        if client_form.is_valid() and agg_form.is_valid():
            client = client_form.save()
            if not client.is_available():
                raise Exception("Client not available")
            aggregate = agg_form.save(commit=False)
            aggregate.client = client
            aggregate.save()
            agg_form.save_m2m()
            # Add current user as owner for the aggregate
            admin_info, created = AggregateAdminInfo.objects.get_or_create(
                admin=request.user,
            )
            aggregate.admins_info.add(admin_info)
            err = aggregate.setup_new_aggregate(request.META['HTTP_HOST'])
            if err:
                transaction.rollback()
                if agg_id:
                    msg = "Problem setting up the updated aggregate. %s" % err
                else:
                    msg = "Problem setting up the new aggregate. %s" % err
                DatedMessage.objects.post_message_to_users(
                    msg, pk=request.user.pk,
                )
                print err
            else:
                aggregate.save()
            return HttpResponseRedirect(reverse("aggregate_all"))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    available = aggregate.check_status if aggregate else False
    return simple.direct_to_template(
        request,
        template="openflow/aggregate_crud.html",
        extra_context={
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            "available": available,
        },
    )
    
def aggregate_delete(request, agg_id):
    return create_update. \
            delete_object(request,
                          OpenFlowAggregate,
                          reverse("aggregate_all"),
                          agg_id,
                          template_name="openflow/aggregate_confirm_delete.html")
