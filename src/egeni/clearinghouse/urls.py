from django.conf.urls.defaults import *
from egeni.clearinghouse.models import AggregateManager

info_dict = {
    'queryset': AggregateManager.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', info_dict, 'index'),
    url(r'^(?P<am_id>\d+)/detail/$', 'egeni.clearinghouse.views.aggmgr_detail', name='am_details'),
    (r'^(?P<am_id>\d+)/detail/update/$', 'egeni.clearinghouse.views.aggmgr_update'),
    (r'^create/$', 'egeni.clearinghouse.views.create'),
    (r'^(?P<object_id>\d+)/delete/$', 'egeni.clearinghouse.views.delete'),
    url(r'^(?P<aggMgr_id>\d+)/switch/(?P<node_id>[0-9a-zA-Z]+)/$', 'egeni.clearinghouse.views.node_detail', name='node_details'),
    (r'^(?P<aggMgr_id>\d+)/switch/(?P<node_id>[0-9a-zA-Z]+)/reserve/$', 'egeni.clearinghouse.views.node_reserve'),
)
