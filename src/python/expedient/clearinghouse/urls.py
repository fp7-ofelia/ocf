'''
@author: jnaous
'''
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'expedient.clearinghouse.views.home', name='home'),
    
    (r'^users/', include('expedient.clearinghouse.users.urls')),
    (r'^aggregate/', include('expedient.clearinghouse.aggregate.urls')),
    (r'^project/', include('expedient.clearinghouse.project.urls')),
    (r'^slice/', include('expedient.clearinghouse.slice.urls')),
    (r'^openflow/', include('openflow.plugin.urls')),
    (r'^expedient_geni/', include('expedient_geni.urls')),
    (r'^planetlab/', include('expedient_geni.planetlab.urls')),
    (r'^messages/', include('expedient.common.messaging.urls')),
    (r'^permissions/', include('expedient.common.permissions.urls')),
    (r'^roles/', include('expedient.clearinghouse.roles.urls')),
    (r'^permissionmgmt/', include('expedient.clearinghouse.permissionmgmt.urls')),
    (r'^admin/', include(admin.site.urls)),

    # TODO: Change to the following after 0.8 of registration is out
    # (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/register/$',
        'expedient.clearinghouse.users.views.register',
        name='registration_register'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        'expedient.clearinghouse.users.views.activate',
        name='registration_activate'),
    url(r'^accounts/register/complete/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    (r'^accounts/', include('registration.urls')),

    # TODO: Remove after testing
    (r'^dummyom/', include('openflow.dummyom.urls')),
)


# Add the plugin URLs:
for plugin in getattr(settings, "UI_PLUGINS", []):
    urlpatterns += patterns('', (r'%s/' % plugin[1], include(plugin[2])))

def get_static_url(name, path=""):
    static_file_tuple = (
        r'^%s%s/(?P<path>.*)$' % (settings.MEDIA_URL[1:], path),
        'django.views.static.serve',
        {'document_root': "%s%s" % (settings.MEDIA_ROOT, path)})
    return url(*static_file_tuple, name=name)

urlpatterns += patterns('',
    get_static_url("img_media", '/img'),
    get_static_url("css_media", '/css'),
    get_static_url("js_media", "/js"),
)
