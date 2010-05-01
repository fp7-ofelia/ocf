from django.conf.urls.defaults import include, patterns
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}, 'home'),
    
    (r'^gapi_tester/', include('clearinghouse.gapi_tester.urls')),
    (r'^users/', include('clearinghouse.users.urls')),
    (r'^aggregate/', include('clearinghouse.aggregate.urls')),
    (r'^openflow/', include('clearinghouse.openflow.urls')),
    (r'^messages/', include('clearinghouse.messaging.urls')),
    
    (r'^admin/', include(admin.site.urls)),

    # TODO Change to the following after 0.8 of registration is out
    # (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('registration.urls')),

    # TODO: Serve static content, should be removed in production deployment
    # serve from another domain to speed up connections (no cookies needed)
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
