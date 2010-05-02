from django.views.generic import simple, list_detail, date_based, create_update
from clearinghouse.messaging.models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseServerError
from django.core.urlresolvers import reverse
from clearinghouse.openflow.forms import OpenFlowAggregateForm
from clearinghouse.openflow.models import OpenFlowAdminInfo
from clearinghouse.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyForm

def aggregate_create(request):
    '''
    Create a new OpenFlow Aggregate.
    '''
    
    if request.method == "GET":
        agg_form = OpenFlowAggregateForm()
        client_form = PasswordXMLRPCServerProxyForm()
        print client_form.as_table()
    elif request.method == "POST":
        agg_form = OpenFlowAggregateForm(request.POST)
        client_form = PasswordXMLRPCServerProxyForm(request.POST)
        
        if client_form.is_valid() and agg_form.is_valid():
            client = client_form.save()
            agg = agg_form.save(commit=False)
            agg.client = client
            agg.save()
            agg_form.save_m2m()
            # Add current user as owner for the aggregate
            admin_info, created = OpenFlowAdminInfo.objects.get_or_create(
                user=request.user,
            )
            print admin_info
            print agg.admins_info
            agg.admins_info.add(admin_info)
            err = agg.setup_new_aggregate(request.META['HTTP_HOST'])
            if err:
                raise Exception(err)
            
            agg.save()
            return HttpResponseRedirect(reverse("aggregate_all"))
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
