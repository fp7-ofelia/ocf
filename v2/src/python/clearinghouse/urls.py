from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}, 'home'),
    
    (r'^users/', include('clearinghouse.users.urls')),
    (r'^aggregate/', include('clearinghouse.aggregate.urls')),
    (r'^openflow/', include('clearinghouse.openflow.urls')),
    (r'^messages/', include('clearinghouse.messaging.urls')),
    
    # TODO: Remove after testing
    (r'^dummyom/', include('clearinghouse.dummyom.urls')),
    
    (r'^admin/', include(admin.site.urls)),

    # TODO: Change to the following after 0.8 of registration is out
    # (r'^accounts/', include('registration.backends.default.urls')),
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
