'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url
from expedient.common.rpc4django.utils import rpc_url
from expedient.clearinghouse.geni.planetlab.models import PlanetLabAggregate

urlpatterns = patterns('geni.views',
    url(r'^aggregate/create/$', 'aggregate_create', kwargs={"agg_model": PlanetLabAggregate}, name='planetlab_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_edit', kwargs={"agg_model": PlanetLabAggregate}, name='planetlab_aggregate_edit'),
)
