from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # TODO Change to the following after 0.8 of registration is out
    # (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('registration.urls')),

    # TODO: Serve static content, should be removed in production deployment
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    (r'^admin/', include(admin.site.urls)),
)
