from django.conf.urls.defaults import *
from egeni.clearinghouse.models import AggregateManager

info_dict = {
    'queryset': AggregateManager.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', info_dict, 'index'),
    url(r'^(?P<object_id>\d+)/detail/$', 'django.views.generic.list_detail.object_detail', info_dict, name='details'),
    (r'^create/$', 'egeni.clearinghouse.views.create'),
    (r'^(?P<object_id>\d+)/delete/$', 'egeni.clearinghouse.views.delete'),
    (r'^(?P<aggMgr_id>\d+)/switch/(?P<node_id>[0-9a-zA-Z]+)/$', 'egeni.clearinghouse.views.node_detail'),
)
