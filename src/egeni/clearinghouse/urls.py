from django.conf.urls.defaults import *
from egeni.clearinghouse.models import AggregateManager

urlpatterns = patterns('egeni.clearinghouse.views',
    url(r'^$', 'home', name='home'),
    url(r'^(?P<slice_id>\w+)/slice_detail/$', 'slice_detail', name='slice_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/$', 'slice_flash_detail', name='slice_flash_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/topo/$', 'slice_get_topo', name='slice_get_topo'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/img/(?P<img_name>[\w.]+)$', 'slice_get_img', name='slice_get_img'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.jar$', 'slice_get_plugin', name='slice_get_plugin'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.xsd$', 'slice_get_xsd', name='slice_get_xsd'),
#    url(r'^aggmgr/(?P<am_id>\d+)/$', 'aggmgr_detail', name='am_detail'),
#    (r'^aggmgr/create/$', 'am_create'),
)

#urlpatterns += patterns('django.views.generic',
#    (r'^aggmgr/$', 'list_detail.object_list', {'queryset': AggregateManager.objects.all()}),
#    (r'^aggmgr/(?P<object_id>\d+)/delete/$', 'create_update.delete_object', 
#     {'model': AggregateManager, 'post_delete_redirect':  '../../'}),
#)
