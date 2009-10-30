from django.conf.urls.defaults import *
from egeni.clearinghouse.models import *

urlpatterns = patterns('django.views.generic',
    url(r'^$', 'simple.direct_to_template', 
        {'template': 'clearinghouse/home.html',
         'extra_context': {'aggmgr_count': AggregateManager.objects.count(),
                           'node_count': Node.objects.count(),
                           'link_count': Link.objects.count(),
                           'slice_count': Slice.objects.count(),
                           'user_count': User.objects.count(),
                           }
        },
        name='home'),
#    (r'^aggmgr/$', 'list_detail.object_list', {'queryset': AggregateManager.objects.all()}),
#    (r'^aggmgr/(?P<object_id>\d+)/delete/$', 'create_update.delete_object', 
#     {'model': AggregateManager, 'post_delete_redirect':  '../../'}),
)

urlpatterns += patterns('egeni.clearinghouse.views',
    url(r'^slice_home/$', 'slice_home', name='slice_home'),
    url(r'^(?P<slice_id>\w+)/slice_detail/$', 'slice_detail', name='slice_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/$', 'slice_flash_detail', name='slice_flash_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/confirm$', 'slice_resv_confirm', name='slice_resv_confirm'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/topo/$', 'slice_get_topo', name='slice_get_topo'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/img/(?P<img_name>[\w.]+)$', 'slice_get_img', name='slice_get_img'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.jar$', 'slice_get_plugin', name='slice_get_plugin'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.xsd$', 'slice_get_xsd', name='slice_get_xsd'),
#    url(r'^aggmgr/(?P<am_id>\d+)/$', 'aggmgr_detail', name='am_detail'),
#    (r'^aggmgr/create/$', 'am_create'),
)
