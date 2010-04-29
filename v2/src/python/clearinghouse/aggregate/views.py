from django.views.generic import list_detail, date_based, create_update
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from clearinghouse.aggregate.models import Aggregate

def list_aggs(request, number=None):
    '''
    Get a list of aggregates.
    '''
    
    return list_detail.object_list(
        request,
        queryset=Aggregate.objects.all(),
        template_name="aggregate/list.html",
        template_object_name="aggregate",
    )
    
def create(request):
    '''
    Create a new aggregate and connect to it.
    '''
    pass
