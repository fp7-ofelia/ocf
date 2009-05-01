from django.conf.urls.defaults import *
from egeni.clearinghouse.models import AggregateManager

info_dict = {
    'queryset': AggregateManager.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', info_dict, 'index'),
    url(r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict, 'details'),
    (r'^create/$', 'egeni.clearinghouse.views.create'),
    (r'^(?P<object_id>\d+)/delete/$', 'egeni.clearinghouse.views.delete'),
    (r'^(?P<object_id>\d+)/(?P<func_name>[a-zA-Z_]*)/$', 'egeni.clearinghouse.views.call_func'),
)
