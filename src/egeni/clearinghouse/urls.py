from django.conf.urls.defaults import *
from egeni.clearinghouse.models import *
from django.core.urlresolvers import reverse

################## General #########################
urlpatterns = patterns('django.views.generic',
    url(r'help/^$', 'simple.direct_to_template', {'template': 'clearinghouse/help.html'}, name='help'),
)

urlpatterns += patterns('egeni.clearinghouse.views',
    url(r'^$', 'home', name='home'),
)

################## Slices #########################
urlpatterns += patterns('egeni.clearinghouse.slice_views',
    url(r'^slice_home/$', 'slice_home', name='slice_home'),
    url(r'^(?P<slice_id>\w+)/slice_detail/$', 'slice_detail', name='slice_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/$', 'slice_flash_detail', name='slice_flash_detail'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/confirm$', 'slice_resv_confirm', name='slice_resv_confirm'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/topo/$', 'slice_get_topo', name='slice_get_topo'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/img/(?P<img_name>[\w.]+)$', 'slice_get_img', name='slice_get_img'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.jar$', 'slice_get_plugin', name='slice_get_plugin'),
    url(r'^(?P<slice_id>\w+)/slice_flash_detail/plugin.xsd$', 'slice_get_xsd', name='slice_get_xsd'),
)

################## Aggregate Managers #########################
urlpatterns += patterns('egeni.clearinghouse.aggmgr_views',
    url(r'^aggmgr/$', 'home', name='aggmgr_admin_home'),
    url(r'^aggmgr/(?P<am_id>\d+)/detail/$', 'detail', name='am_detail'),
)

urlpatterns += patterns('django.views.generic',
    url(r'aggmgr/saved/^$', 'simple.direct_to_template', {'template': 'clearinghouse/aggregatemanager_saved.html'}, name='aggmgr_saved'),
    url(r'^aggmgr/(?P<object_id>\d+)/delete/$',
        'create_update.delete_object', 
        {'model': AggregateManager,
         'post_delete_redirect': "../../"},
        name="aggmgr_delete"),
)
