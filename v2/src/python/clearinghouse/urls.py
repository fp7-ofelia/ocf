from django.conf.urls.defaults import include, patterns
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}, 'home'),
    
    (r'^users/', include('clearinghouse.users.urls')),
    
    (r'^admin/', include(admin.site.urls)),

    # GENI API RPC URL
    (r'^gapi$', 'rpc4django.views.serve_rpc_request'),
    
    # TODO Change to the following after 0.8 of registration is out
    # (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('registration.urls')),

    # TODO: Serve static content, should be removed in production deployment
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
