'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.slice.models import Slice
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch

def home(request, slice_id):
    slice = get_object_or_404(Slice, id=slice_id)
    return simple.direct_to_template(
        request,
        template="html/select_resources.html",
        extra_context={
            "openflow_aggs": OpenFlowAggregate.objects.filter(
                slice=slice,
            ),
            "ofswitch_class": OpenFlowSwitch,
        },
    )
