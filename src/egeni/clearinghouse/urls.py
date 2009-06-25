from django.conf.urls.defaults import *
from egeni.clearinghouse.models import AggregateManager

urlpatterns = patterns('egeni.clearinghouse.views',
    url(r'^$', 'home', name='home'),
    url(r'^(?P<slice_id>\w+)/slice_detail/$', 'slice_detail', name='slice_detail'),
    url(r'^(?P<slice_id>\w+)/(?P<am_id>\d+)/selectnodes/$', 'resv_sel_nodes', name='sel_nodes'),
#    url(r'^aggmgr-(?P<am_id>\d+)/detail/$', 'aggmgr_detail', name='am_detail'),
#    (r'^create/$', 'create'),
#    (r'^(?P<object_id>\d+)/delete/$', 'delete'),
#    url(r'^(?P<aggMgr_id>\d+)/node/(?P<node_id>\w+)/$', 'node_detail', name='node_detail'),
#    (r'^(?P<aggMgr_id>\d+)/node/(?P<node_id>\w+)/reserve/$', 'node_reserve'),
)

