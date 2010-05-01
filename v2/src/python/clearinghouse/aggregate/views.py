from django.views.generic import list_detail, date_based, create_update
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from clearinghouse.aggregate.models import Aggregate
from clearinghouse.aggregate.forms import AggregateTypeForm
from django.contrib.contenttypes.models import ContentType
import sys

def list_aggs(request, obj_id=None):
    '''
    Get a list of aggregates. obj_id specifies id to highlight.
    '''
    
    qs = Aggregate.objects.all()
    qs.select_related()
    
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
    
    print form.as_p()
    
    return list_detail.object_list(
        request,
        queryset=qs,
        template_name="aggregate/list.html",
        template_object_name="aggregate",
        extra_context={
            'form': form,
            'highlight_id': obj_id,
        },
    )
