from django.conf.urls.defaults import *
from egeni.clearinghouse.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

################## General #########################
urlpatterns = patterns('django.views.generic',
    url(r'^help/$', 'simple.direct_to_template', {'template': 'clearinghouse/help.html'}, name='help'),
)

urlpatterns += patterns('egeni.clearinghouse.views',
    url(r'^$', 'home', name='home'),
    url(r'img/(?P<img_name>[\w.-]+)$', 'get_img', name='get_img')
)

################## Slices #########################
urlpatterns += patterns('egeni.clearinghouse.slice_views',
    url(r'^slice/$', 'slice_home', name='slice_home'),
    url(r'^slice/(?P<slice_id>\w+)/select/aggregates/$', 'slice_select_aggregates', name='slice_select_aggregates'),
    url(r'^slice/(?P<slice_id>\w+)/select/topo/$', 'slice_select_topo', name='slice_select_topo'),
    url(r'^slice/(?P<slice_id>\w+)/select/topo/topo.xml$', 'slice_get_topo_xml', name='slice_get_topo_xml'),
    url(r'^slice/(?P<slice_id>\w+)/select/topo/plugin.jar$', 'slice_get_plugin', name='slice_get_plugin'),
    url(r'^slice/(?P<slice_id>\w+)/select/openflow/$', 'slice_select_openflow', name='slice_select_openflow'),
    url(r'^slice/(?P<slice_id>\w+)/resv/summary$', 'slice_resv_summary', name='slice_resv_summary'),
    url(r'^slice/(?P<slice_id>\w+)/resv/confirm$', 'slice_resv_confirm', name='slice_resv_confirm'),
)

urlpatterns += patterns('django.views.generic',
    url(r'^slice/(?P<object_id>\d+)/delete/$',
        'create_update.delete_object', 
        {'model': Slice,
         'post_delete_redirect': "../../"},
        "slice_delete"),
)

################## Aggregate Managers #########################
urlpatterns += patterns('egeni.clearinghouse.aggmgr_views',
    url(r'^aggmgr/$', 'home', name='aggmgr_admin_home'),
    url(r'^aggmgr/(?P<am_id>\d+)/detail/$', 'detail', name='am_detail'),
    url(r'^aggmgr/(?P<am_id>\d+)/saved/$', 'saved', name='aggmgr_saved'),
    url(r'^aggmgr/(?P<am_id>\d+)/delete/$', 'delete', name="aggmgr_delete"),
)

################## Users #########################
urlpatterns += patterns('egeni.clearinghouse.user_views',
    url(r'^user/$', 'home', name='user_admin_home'),
    url(r'^user/(?P<user_id>\d+)/detail/$', 'detail', name='user_detail'),
    url(r'^user/(?P<user_id>\d+)/saved/$', 'saved', name='user_saved'),
    url(r'^user/(?P<user_id>\d+)/delete/$', 'delete', name="user_delete"),
)
