from django.views.generic import simple, list_detail, date_based, create_update
from clearinghouse.messaging.models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from clearinghouse.openflow.forms import OpenFlowAggregateForm
from clearinghouse.xmlrpc.forms import PasswordXMLRPCClientForm

def aggregate_create(request):
    '''
    Create a new OpenFlow Aggregate.
    '''
    
    if request.method == "GET":
        agg_form = OpenFlowAggregateForm()
        client_form = PasswordXMLRPCClientForm()
        print client_form.as_table()
    elif request.method == "POST":
        agg_form = OpenFlowAggregateForm(request.POST)
        client_form = PasswordXMLRPCClientForm(request.POST)
        
        if client_form.is_valid() and agg_form.is_valid():
            client = client_form.save()
            agg = agg_form.save(commit=False)
            agg.client = client
            agg.save()
            agg_form.save_m2m()
            return HttpResponseRedirect(reverse("openflow_aggregate_edit",
                                                kwargs={'obj_id': agg.id}))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    return simple.direct_to_template(
        request,
        template="openflow/aggregate_create.html",
        extra_context={
            "agg_form": agg_form,
            "client_form": client_form,
        },
    )
