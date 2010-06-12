'''
@author jnaous
'''
from django.views.generic import list_detail
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.aggregate.forms import AggregateTypeForm

def list_aggs(request, obj_id=None):
    '''
    Get a list of aggregates. obj_id specifies id to highlight.
    '''
    
    # Only list the aggregates of which the user is admin
    qs = Aggregate.objects.filter(admins_info__admin=request.user)
    
    if request.method == "GET":
        form = AggregateTypeForm()
    elif request.method == "POST":
        form = AggregateTypeForm(request.POST)
        if form.is_valid():
            [module, sep, name] = form.cleaned_data['type'].rpartition(".")
            _temp = __import__(module, globals(), locals(), [name])
            model = getattr(_temp, name)
            return HttpResponseRedirect(model.get_create_url())
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    return list_detail.object_list(
        request,
        queryset=qs,
        template_name="expedient/clearinghouse/aggregate/list.html",
        template_object_name="aggregate",
        extra_context={
            'form': form,
            'highlight_id': obj_id,
        },
    )

