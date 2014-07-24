'''
@author: jnaous
'''
from django.conf.urls.defaults import *
from expedient.clearinghouse.geni.gopenflow.models import GCFOpenFlowAggregate

urlpatterns = patterns('expedient.clearinghouse.geni.gopenflow.views',
    url(r'^aggregate/create/$', 'aggregate_create', name='gopenflow_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_edit', name='gopenflow_aggregate_edit'),
    url(r'^aggregate/(?P<agg_id>\d+)/links/$', 'aggregate_add_links', name='gopenflow_aggregate_add_links'),
    url(r'^aggregate/(?P<agg_id>\d+)/slice/(?P<slice_id>\d+)/add/$', 'aggregate_add_to_slice', name='gopenflow_aggregate_slice_add'),
)
