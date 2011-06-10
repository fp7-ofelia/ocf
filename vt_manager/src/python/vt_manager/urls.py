from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from common.rpc4django.utils import rpc_url
admin.autodiscover()

'''
Dynamic content
'''

urlpatterns = patterns('',
    ##Main entry point
    url(r'^dashboard$', 'vt_manager.controller.users.urlHandlers.dashboard', name="dashboard"),
    (r'^$', 'vt_manager.controller.users.urlHandlers.index'),
#    url(r'^servers/net/update/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_net_update', name='servers_net_update'),
    
    ##Server management
    url(r'^servers/add/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_crud', name='servers_create'),
    url(r'^servers/(?P<server_id>\d+)/edit/$', 'vt_manager.controller.dispatchers.GUIdispatcher.servers_crud', name='edit_server'),
    url(r'^servers/admin/$', 'vt_manager.controller.dispatchers.GUIdispatcher.admin_servers', name='admin_servers'),
    url(r'^servers/(?P<server_id>\d+)/delete/$', 'vt_manager.controller.dispatchers.GUIdispatcher.delete_server', name='delete_server'),
    url(r'^servers/(?P<server_id>\d+)/virtual_machines/(?P<vm_id>\d+)/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.action_vm', name='action_vm'),
    url(r'^servers/(?P<server_id>\d+)/subscribeEthernetRanges/$', 'vt_manager.controller.dispatchers.GUIdispatcher.subscribeEthernetRanges', name='subscribeEthernetRanges'),
    url(r'^servers/(?P<server_id>\d+)/subscribeIp4Ranges/$', 'vt_manager.controller.dispatchers.GUIdispatcher.subscribeIp4Ranges', name='subscribeIp4Ranges'),

    ##Networking
    url(r'^networking/$', 'vt_manager.controller.dispatchers.GUIdispatcher.networkingDashboard', name='networkingDashboard'),

    #Ip4
    url(r'^networking/ip4/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageIp4', name='ip4Ranges'),
    url(r'^networking/ip4/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageIp4', name='showIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageIp4', name='createIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageIp4', name='manageIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/(?P<rangeId>\d+)/(?P<ip4Id>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageIp4', name='manageIp4RangeExcluded'),



    #Ethernet
    url(r'^networking/ethernet/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageEthernet', name='macRanges'),
    url(r'^networking/ethernet/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageEthernet', name='showMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageEthernet', name='createMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageEthernet', name='manageMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/(?P<rangeId>\d+)/(?P<macId>\d+)/$', 'vt_manager.controller.dispatchers.GUIdispatcher.manageEthernet', name='manageMacRangeExcluded'),


    #User mgmt 
    url(r'^change_profile$', 'vt_manager.controller.users.urlHandlers.change_profile', name="change_profile"),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),

    #RPC
    rpc_url(r'^xmlrpc/agent$', name='agent'),
    rpc_url(r'^xmlrpc/plugin$', name='plugin'),
    rpc_url(r'^xmlrpc/.*$', name='root'),
)


'''
Static content
'''

static_image_file_tuple = (r'^%s/(?P<path>.*)$' % str(settings.MEDIA_URL[1:]+"/images/"),
                     'django.views.static.serve',
                     {'document_root': "%s" % settings.MEDIA_ROOT})

static_css_file_tuple = (r'^%s/(?P<path>.*)$' % str(settings.MEDIA_URL[1:]+"/css/"),
                     'django.views.static.serve',
                     {'document_root': "%s" % settings.MEDIA_ROOT})

static_js_file_tuple = (r'^%s/(?P<path>.*)$' % str(settings.MEDIA_URL[1:]+"/js/"),
                     'django.views.static.serve',
                     {'document_root': "%s" % settings.MEDIA_ROOT})

static_fancybox_tuple = (r'^%s/(?P<path>.*)$' % str(settings.MEDIA_URL[1:]+"/fancybox/"),
                     'django.views.static.serve',
                     {'document_root': "%s" % settings.MEDIA_ROOT})

urlpatterns += patterns('',
    # TODO: Serve static content, should be removed in production deployment
    # serve from another domain to speed up connections (no cookies needed)
    url(*static_image_file_tuple, name="img_media"),
    url(*static_css_file_tuple, name="css_media"),
    url(*static_js_file_tuple, name="js_media"),
    url(*static_fancybox_tuple, name="fancybox"),
)
