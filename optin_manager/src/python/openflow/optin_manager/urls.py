from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from expedient.common.rpc4django.utils import rpc_url

from openflow.common.utils.OptinThemeManager import OptinThemeManager
OptinThemeManager.initialize()


admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'openflow.optin_manager.users.views.index'),
    url(r'^dashboard$', 'openflow.optin_manager.users.views.dashboard', name="dashboard"),

    url(r'^change_profile$', 'openflow.optin_manager.users.views.change_profile', name="change_profile"),

    (r'^controls/', include('openflow.optin_manager.controls.urls')),

    (r'^opts/', include('openflow.optin_manager.opts.urls')),

    (r'^admin_manager/', include('openflow.optin_manager.admin_manager.urls')),

    (r'^xmlrpc/', include('openflow.optin_manager.xmlrpc_server.urls')),
    
    # For testing
    (r'^dummyfv/', include('openflow.optin_manager.dummyfv.urls')),
    
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/', include('registration.urls')),

    # sfa
    rpc_url(r'^xmlrpc/sfa/?$', name='optin_sfa'),

)

#static_file_tuple = (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL[1:],
#                     'django.views.static.serve',
#                     {'document_root': "%s" % settings.MEDIA_ROOT})
#static_js_tuple = (r'^%s/(?P<path>.*)$' % str(settings.MEDIA_URL[1:]+"/js/"),
#                    'django.views.static.serve',
#                     {'document_root': "%s" % settings.MEDIA_ROOT})


#urlpatterns += patterns('',
   # TODO: Serve static content, should be removed in production deployment
    # serve from another domain to speed up connections (no cookies needed)
#    url(*static_file_tuple, name="img_media"),
#    url(*static_file_tuple, name="css_media"),
#    url(*static_js_tuple, name="js_media"),)


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
    get_static_url("img_media", "/default"),
    get_static_url("css_media", "/default"),
    get_static_url("js_media", "/default/js"),
)

'''
Static theme content
'''
img_theme_tuple = OptinThemeManager.getStaticThemeTuple("img_media")
css_theme_tuple = OptinThemeManager.getStaticThemeTuple("css_media")
js_theme_tuple = OptinThemeManager.getStaticThemeTuple("js_media")

urlpatterns += patterns('',
    get_static_url(img_theme_tuple[0],img_theme_tuple[1]),
    get_static_url(css_theme_tuple[0],css_theme_tuple[1]),
    get_static_url(js_theme_tuple[0],js_theme_tuple[1]),
)
