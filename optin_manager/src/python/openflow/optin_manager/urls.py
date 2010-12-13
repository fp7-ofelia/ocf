from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

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
