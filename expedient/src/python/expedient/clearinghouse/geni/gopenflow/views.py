'''
Created on Oct 12, 2010

@author: jnaous
'''
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.geni.gopenflow.models import GCFOpenFlowAggregate
from openflow.plugin.views import handle_add_links, handle_add_to_slice
from django.core.urlresolvers import reverse
from expedient.clearinghouse.slice.models import Slice
import expedient.clearinghouse.geni.views as eg_views

def aggregate_add_links(request, agg_id):
    """
    Show page to add static connections to other aggregates.
    """
    aggregate = get_object_or_404(GCFOpenFlowAggregate, id=agg_id)
    
    return handle_add_links(
        request, aggregate,
        extra_context={
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("Update GCF OpenFlow Aggregate",
                 reverse("gopenflow_aggregate_edit", args=[agg_id])),
                ("Edit Static Links",
                 reverse("gopenflow_aggregate_add_links", args=[agg_id])),
            ),
        }
    )
    
def aggregate_add_to_slice(request, agg_id, slice_id):
    """
    Add the aggregate to the slice. Check if the slice already has
    OpenFlowSliceInfo information related to it. If there is, then reuse that.
    """
    
    aggregate = get_object_or_404(GCFOpenFlowAggregate, id=agg_id)
    slice = get_object_or_404(Slice, id=slice_id)
    
    return handle_add_to_slice(request, aggregate, slice)

def aggregate_create(request):
    return eg_views.aggregate_create(
        request, GCFOpenFlowAggregate,
        lambda inst: reverse("gopenflow_aggregate_add_links", args=[inst.id]))
    
def aggregate_edit(request, agg_id):
    return eg_views.aggregate_edit(
        request, agg_id, GCFOpenFlowAggregate,
        lambda inst: reverse("gopenflow_aggregate_add_links", args=[inst.id]))
