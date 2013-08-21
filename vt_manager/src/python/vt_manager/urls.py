from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from common.rpc4django.utils import rpc_url
import re 
admin.autodiscover()

from vt_manager.utils.ThemeManager import ThemeManager
from vt_manager.communication.southCommInterface import *
from vt_manager.communication.northCommInterface import *
from vt_manager.communication.sfaCommunication import *

'''
Load Themes
'''
ThemeManager.initialize()

'''
Dynamic content
'''
urlpatterns = patterns('',
    ##Main entry point
    url(r'^dashboard$', 'vt_manager.controller.users.urlHandlers.dashboard', name="dashboard"),
    (r'^$', 'vt_manager.controller.users.urlHandlers.index'),
#    url(r'^servers/net/update/$', 'vt_manager.controller.dispatchers.ui.GUIdispatcher.servers_net_update', name='servers_net_update'),

    #Policy Engine
    url(r'^policies/(?P<table>\w+)/add/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.policy_create', name="policy_create"),    
    url(r'^policies/(?P<table>\w+)/edit/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.policy_edit', name="policy_edit"),
    url(r'^policies/(?P<table_uuid>\w+)/delete/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.policy_delete', name="policy_delete"),
    url(r'^policies/(?P<table_name>\w+)/add/rules/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_create', name="rule_create"),   
    url(r'^policies/(?P<table_name>\w+)/delete/rules/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_delete', name="rule_delete"),
    url(r'^policies/(?P<table_name>\w+)/edit/rules/(?P<rule_uuid>\w+)/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_edit', name="rule_edit"),
    url(r'^policies/$', 'vt_manager.controller.dispatchers.ui.PolicyDispatcher.rule_table_view', name="rule_table_view"),
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
    rpc_url(r'^xmlrpc/agent/?$', name='agent'),
    rpc_url(r'^xmlrpc/plugin/?$', name='plugin'),
    rpc_url(r'^xmlrpc/sfa/?$', name='sfa'),
    #rpc_url(r'^xmlrpc/.*$', name='root'),
)

def get_static_url(name, path=""):
    static_file_tuple = (
        r'^%s%s/(?P<path>.*)$' % (settings.MEDIA_URL[1:], path),
        'django.views.static.serve',
        {'document_root': "%s%s" % (settings.MEDIA_ROOT, path)})
    return url(*static_file_tuple, name=name)

'''
Static content
'''
urlpatterns += patterns('',
    get_static_url("img_media", "/default/images"),
    get_static_url("css_media", "/default/css"),
    get_static_url("js_media", "/default/js"),
    get_static_url("fancybox", "/default/fancybox"),
)

'''
Static theme content
'''
img_theme_tuple = ThemeManager.getStaticThemeTuple("img_media")
css_theme_tuple = ThemeManager.getStaticThemeTuple("css_media")
js_theme_tuple = ThemeManager.getStaticThemeTuple("js_media")
fancybox_theme_tuple = ThemeManager.getStaticThemeTuple("fancybox")

urlpatterns += patterns('',
    get_static_url(img_theme_tuple[0],img_theme_tuple[1]), 
    get_static_url(css_theme_tuple[0],css_theme_tuple[1]),
    get_static_url(js_theme_tuple[0],js_theme_tuple[1]),
    get_static_url(fancybox_theme_tuple[0],fancybox_theme_tuple[1]),
)



