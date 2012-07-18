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
#    url(r'^servers/net/update/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.servers_net_update', name='servers_net_update'),

    #Policy Engine
    url(r'^policies/policy_create/(?P<table>\w+)/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.policy_create', name="policy_create"),    
    url(r'^policies/create$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_create', name="rule_create"),   
    url(r'^policies/delete$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_delete', name="rule_delete"),
    url(r'^policies/edit/(?P<rule_uuid>\w+)/(?P<table_name>\w+)/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_edit', name="rule_edit"),
    url(r'^policies/rule_table_view$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_table_view', name="rule_table_view"),
    url(r'^policies/update_ruleTable_policy$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.update_ruleTable_policy', name="update_ruleTable_policy"),
    url(r'^policies/enable_disable/(?P<rule_uuid>\w+)/(?P<table_name>\w+)/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.enable_disable', name="enable_disable"),
    url(r'^condition_create/(?P<TableName>\w+)/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.condition_create', name="condition_create"),


    ##Server management
    url(r'^servers/add/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.servers_crud', name='servers_create'),
    url(r'^servers/(?P<server_id>\d+)/edit/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.servers_crud', name='edit_server'),
    url(r'^servers/admin/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.admin_servers', name='admin_servers'),
    url(r'^servers/(?P<server_id>\d+)/delete/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.delete_server', name='delete_server'),
    url(r'^servers/(?P<server_id>\d+)/virtual_machines/(?P<vm_id>\d+)/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.action_vm', name='action_vm'),
    url(r'^servers/(?P<server_id>\d+)/subscribeEthernetRanges/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.subscribeEthernetRanges', name='subscribeEthernetRanges'),
    url(r'^servers/(?P<server_id>\d+)/subscribeIp4Ranges/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.subscribeIp4Ranges', name='subscribeIp4Ranges'),
#    url(r'^servers/(?P<server_id>\d+)/vms_status/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.check_vms_status', name='check_vms_status'),
    url(r'^servers/(?P<server_id>\d+)/list_vms/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.list_vms', name='list_vms'),


    ##Networking
    url(r'^networking/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.networkingDashboard', name='networkingDashboard'),

    #Ip4
    url(r'^networking/ip4/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageIp4', name='ip4Ranges'),
    url(r'^networking/ip4/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageIp4', name='showIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageIp4', name='createIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageIp4', name='manageIp4Range'),
    url(r'^networking/ip4/(?P<action>\w+)/(?P<rangeId>\d+)/(?P<ip4Id>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageIp4', name='manageIp4RangeExcluded'),



    #Ethernet
    url(r'^networking/ethernet/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageEthernet', name='macRanges'),
    url(r'^networking/ethernet/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageEthernet', name='showMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageEthernet', name='createMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/(?P<rangeId>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageEthernet', name='manageMacRange'),
    url(r'^networking/ethernet/(?P<action>\w+)/(?P<rangeId>\d+)/(?P<macId>\d+)/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.manageEthernet', name='manageMacRangeExcluded'),


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
