from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from common.rpc4django.utils import rpc_url
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'vt_manager.controller.users.urlHandlers.index'),
    url(r'^dashboard$', 'vt_manager.controller.users.urlHandlers.dashboard', name="dashboard"),
    url(r'^change_profile$', 'vt_manager.controller.users.urlHandlers.change_profile', name="change_profile"),

    url(r'^servers/net/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_net_settings', name='servers_net_settings'),
    url(r'^servers/net/update/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_net_update', name='servers_net_update'),
    url(r'^servers/add/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_crud', name='servers_create'),
    url(r'^servers/(?P<server_id>\d+)/edit/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_crud', name='edit_server'),
    url(r'^servers/admin/$', 'vt_manager.controller.dispatchers.GUIdispatcher.admin_servers', name='admin_servers'),
    url(r'^servers/(?P<server_id>\d+)/delete/$', 'vt_manager.controller.dispatchers.GUIdispatcher.delete_server', name='delete_server'),
   
    url(r'^servers/(?P<server_id>\d+)/virtual_machines/(?P<vm_id>\d+)/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.action_vm', name='action_vm'),

    rpc_url(r'^xmlrpc/agent$', name='agent'),
    rpc_url(r'^xmlrpc/plugin$', name='plugin'),
    rpc_url(r'^xmlrpc/.*$', name='root'),

    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/', include('registration.urls')),

)

static_file_tuple = (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL[1:],
                     'django.views.static.serve',
                     {'document_root': "%s" % settings.MEDIA_ROOT})
urlpatterns += patterns('',
   # TODO: Serve static content, should be removed in production deployment
    # serve from another domain to speed up connections (no cookies needed)
    url(*static_file_tuple, name="img_media"),
    url(*static_file_tuple, name="css_media"),
)
