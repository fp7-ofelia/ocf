'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url
from expedient_geni.gopenflow.models import GCFOpenFlowAggregate

urlpatterns = patterns('expedient_geni.views',
    url(r'^aggregate/create/$', 'aggregate_create', kwargs={"agg_model": GCFOpenFlowAggregate}, name='gopenflow_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_edit', kwargs={"agg_model": GCFOpenFlowAggregate}, name='gopenflow_aggregate_edit'),
)
