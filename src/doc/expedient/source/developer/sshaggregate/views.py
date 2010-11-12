from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import simple
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.utils import post_message_to_current_user
from sshaggregate.models import SSHAggregate, SSHServer

def aggregate_crud(request, agg_id=None):
    """Show a page for the user to add/edit an SSH aggregate in Expedient."""
    
    return generic_crud(
        request,
        obj_id=agg_id,
        model=SSHAggregate,
        template_object_name="aggregate",
        template="sshaggregate/aggregate_crud.html",
        redirect=lambda inst: reverse(
            aggregate_add_servers, args=[inst.id]),
        success_msg=lambda inst: \
            "Successfully created/updated SSH Aggregate %s" % inst.name,
    )
    
def aggregate_add_servers(request, agg_id):
    """Show a page that allows user to add SSH servers to the aggregate."""
    
    agg = get_object_or_404(SSHAggregate, id=agg_id)
    servers = SSHServer.objects.filter(aggregate__id=agg_id)
    ServerFormSet = modelformset_factory(
        SSHServer, can_delete=True, extra=3,
        fields=["name", "ip_address", "ssh_port"],
    )

    if request.method == "POST":
        formset = ServerFormSet(
            request.POST, queryset=servers)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.aggregate = agg
                instance.save()
            formset.save_m2m()
            post_message_to_current_user(
                "Successfully added/updated servers "\
                "to aggregate %s" % agg.name,
                msg_type=DatedMessage.TYPE_SUCCESS)
            
            return HttpResponseRedirect(request.path)
        
    else:
        formset = ServerFormSet(queryset=servers)

    return simple.direct_to_template(
        request, template="sshaggregate/aggregate_add_servers.html",
        extra_context={"aggregate": agg, "formset": formset})
