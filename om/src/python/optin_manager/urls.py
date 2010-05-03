from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'optin_manager.users.views.index'),
    (r'^dashboard$', 'optin_manager.users.views.dashboard'),

    (r'^flowspace/', include('optin_manager.flowspace.urls')),

    (r'^xmlrpc/', include('optin_manager.xmlrpc_server.urls')),
    # Example:
    # (r'^optin_manager/', include('optin_manager.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
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
