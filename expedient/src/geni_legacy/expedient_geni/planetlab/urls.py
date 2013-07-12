'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url
from common.rpc4django.utils import rpc_url
from geni_legacy.expedient_geni.planetlab.models import PlanetLabAggregate

urlpatterns = patterns('geni_legacy.expedient_geni.views',
    url(r'^aggregate/create/$', 'aggregate_create', kwargs={"agg_model": PlanetLabAggregate}, name='planetlab_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_edit', kwargs={"agg_model": PlanetLabAggregate}, name='planetlab_aggregate_edit'),
)
