#from django.core.urlresolvers import reverse
#from django.forms.models import modelformset_factory
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponseRedirect
#from django.views.generic import simple
#from expedient.common.utils.views import generic_crud
#from expedient.common.messaging.models import DatedMessage
#from expedient.clearinghouse.aggregate.models import Aggregate
#from expedient.clearinghouse.utils import post_message_to_current_user
#from expedient.common.permissions.shortcuts import give_permission_to, must_have_permission
#
#class ResourceController:
#
#    def aggregate_crud(request, agg_id=None):
#    '''
#    Create/update an Virtualization Aggregate.
#    '''
#    if agg_id != None:
#        aggregate = get_object_or_404(VtPlugin, pk=agg_id)
#        client = aggregate.client
#    else:
#        aggregate = None
#        client = None
#
#    extra_context_dict = {}
#    errors = ""
#
#    if request.method == "GET":
#        agg_form = VTAggregateForm(instance=aggregate)
#        client_form = xmlrpcServerProxyForm(instance=client)
#
#    elif request.method == "POST":
#        agg_form = VTAggregateForm(
#            data=request.POST, instance=aggregate)
#       client_form = xmlrpcServerProxyForm(
#            data=request.POST, instance=client)
#
#        if client_form.is_valid() and agg_form.is_valid():
#            # Ping is tried after every field check
#            client = client_form.save(commit=False)
#            s = xmlrpclib.Server('https://'+client.username+':'+client.password+'@'+client.url[8:])
#            try:
#                s.ping('ping')
#            except:
#                errors = "Could not connect to server: username, password or url are not correct"
#                DatedMessage.objects.post_message_to_user(
#                    errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,
#                )
#                extra_context_dict['errors'] = errors
#
#            if not errors:
#                client = client_form.save()
#                aggregate = agg_form.save(commit=False)
#                aggregate.client = client
#                aggregate.save()
#                agg_form.save_m2m()
#                aggregate.save()
#                give_permission_to(
#                   "can_use_aggregate",
#                   aggregate,
#                   request.user,
#                   can_delegate=True
#                )
#                give_permission_to(
#                    "can_edit_aggregate",
#                    aggregate,
#                    request.user,
#                    can_delegate=True
#                )
#                DatedMessage.objects.post_message_to_user(
#                    "Successfully created/updated aggregate %s" % aggregate.name,
#                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,
#                )
#                return HttpResponseRedirect("/")
#    else:
#        return HttpResponseNotAllowed("GET", "POST")
#
#    if not errors:
#        extra_context_dict['available'] = aggregate.check_status() if agg_id else False
#
#    # Updates the dictionary with the common fields
#    extra_context_dict.update({
#            "agg_form": agg_form,
#            "client_form": client_form,
#            "create": not agg_id,
#            "aggregate": aggregate,
#            # Previously commented
#            # "available": available,
#            "breadcrumbs": (
#                ('Home', reverse("home")),
#                ("%s Sample Resource Aggregate" % ("Update" if agg_id else "Add"),
#                 request.path),
#            )
#        })
#
#    return simple.direct_to_template(
#        request,
#        template="aggregate_crud.html",
#        extra_context=extra_context_dict
#    )

