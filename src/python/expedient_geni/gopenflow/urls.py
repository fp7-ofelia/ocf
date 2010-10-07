'''
@author: jnaous
'''
from django.conf.urls.defaults import *
from expedient_geni.gopenflow.models import GCFOpenFlowAggregate

urlpatterns = patterns('',
    url(r'^aggregate/create/$', 'expedient_geni.views.aggregate_create', kwargs={"agg_model": GCFOpenFlowAggregate}, name='gopenflow_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'expedient_geni.views.aggregate_edit', kwargs={"agg_model": GCFOpenFlowAggregate}, name='gopenflow_aggregate_edit'),
)
