'''
@author jnaous
'''
from django.views.generic import list_detail
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.aggregate.forms import AggregateTypeForm

def list_aggs(request, obj_id=None):
    '''
    Get a list of aggregates. obj_id specifies id to highlight. On POST,
    get the type of aggregate to be created and redirect to that model's
    create url.
    '''
    
    qs = Aggregate.objects.all()
    
    if request.method == "GET":
        form = AggregateTypeForm()
    elif request.method == "POST":
        form = AggregateTypeForm(request.POST)
        if form.is_valid():
            model = form.cleaned_data["type"].model_class()
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

