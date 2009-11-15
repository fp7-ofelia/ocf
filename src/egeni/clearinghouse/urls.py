from django.conf.urls.defaults import *
from egeni.clearinghouse.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

################## General #########################
urlpatterns = patterns('django.views.generic',
    url(r'^help/$', 'simple.direct_to_template', {'template': 'clearinghouse/help.html'}, name='help'),
)

urlpatterns += patterns('egeni.clearinghouse.views',
    url(r'^$', 'home', name='home'),
)

urlpatterns += patterns('',
    # TODO: Serve static content, should be removed in production deployment
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
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
    url(r'^slice/(?P<slice_id>\w+)/delete$', 'slice_delete', name='slice_delete'),
    url(r'^slice/(?P<slice_id>\w+)/pl-key.pkey$', 'slice_get_key', name='slice_get_key'),
)

################## Aggregate Managers #########################
urlpatterns += patterns('egeni.clearinghouse.aggmgr_views',
    url(r'^aggmgr/$', 'home', name='aggmgr_admin_home'),
    url(r'^aggmgr/(?P<am_id>\d+)/detail/$', 'detail', name='aggmgr_detail'),
    url(r'^aggmgr/(?P<am_id>\d+)/saved/$', 'saved', name='aggmgr_saved'),
    url(r'^aggmgr/(?P<am_id>\d+)/delete/$', 'delete', name="aggmgr_delete"),
    url(r'^aggmgr/(?P<am_id>\d+)/rspec.xml$', 'rspec', name="aggmgr_rspec"),
)

################## Users #########################
urlpatterns += patterns('egeni.clearinghouse.user_views',
    url(r'^user/$', 'home', name='user_admin_home'),
    url(r'^user/(?P<user_id>\d+)/detail/$', 'detail', name='user_detail'),
    url(r'^user/(?P<user_id>\d+)/saved/$', 'saved', name='user_saved'),
    url(r'^user/(?P<user_id>\d+)/delete/$', 'delete', name="user_delete"),
)

