'''
@author: jnaous
'''
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template
#from expedient.common.utils.plugins.pluginloader import PluginLoader as PLUGIN_LOADER


''' Theme Management '''

from expedient.common.utils.ExpedientThemeManager import ExpedientThemeManager
ExpedientThemeManager.initialize()



admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'expedient.clearinghouse.views.home', name='home'),
    url(r'^help/$',
        direct_to_template,
        {'template': 'help/index.html'},
        name='help'),

#    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '../../static/default/img/favicon.ico'}),    
    (r'^users/', include('expedient.clearinghouse.users.urls')),
    (r'^aggregate/', include('expedient.clearinghouse.aggregate.urls')),
    (r'^project/', include('expedient.clearinghouse.project.urls')),
    (r'^slice/', include('expedient.clearinghouse.slice.urls')),
    (r'^expedient_geni/', include('expedient_geni.urls')),
    (r'^messages/', include('expedient.common.messaging.urls')),
    (r'^permissions/', include('expedient.common.permissions.urls')),
    (r'^roles/', include('expedient.clearinghouse.roles.urls')),
    (r'^permissionmgmt/', include('expedient.clearinghouse.permissionmgmt.urls')),
    (r'^messagecenter/',include('expedient.clearinghouse.messagecenter.urls')),
    (r'^admin/', include(admin.site.urls)),

)

# Password reset url
urlpatterns += patterns('',
    url(r'^accounts/password/reset/$',
        'expedient.clearinghouse.users.views.my_password_reset',
        name='my_password_reset'),
    )
#Registration urls depending on ALLOW_LOCAL_REGISTRATION flag
if settings.ALLOW_LOCAL_REGISTRATION == True:
    urlpatterns += patterns('',
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
    url(r'^accounts/', include('registration.urls')),
    )
else:
    urlpatterns += patterns('',
    url(r'^accounts/register/$',
        ' ',
        name='registration_register'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        ' ',
        name='registration_activate'),
    url(r'^accounts/register/complete/$',
        direct_to_template,
        ' ',
        name='registration_complete'),
    url(r'^accounts/', include('registration.urls')),
    )




# Add the plugin URLs:
for plugin in getattr(settings, "UI_PLUGINS", []):
    urlpatterns += patterns('', (r'^%s/' % plugin[1], include(plugin[2])))

for plugin in getattr(settings, "AGGREGATE_PLUGINS", []):
    urlpatterns += patterns('', (r'^%s/' % plugin[1], include(plugin[2])))

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
    get_static_url("root_media"),
    #get_static_url("/favicon.ico","/img/favicon.ico")
)

# URLs for static content in plugins
urlpatterns += settings.PLUGIN_LOADER.generate_static_content_urls(settings.MEDIA_URL)

'''
Static theme content
'''
img_theme_tuple = ExpedientThemeManager.getStaticThemeTuple("img_media")
css_theme_tuple = ExpedientThemeManager.getStaticThemeTuple("css_media")
js_theme_tuple = ExpedientThemeManager.getStaticThemeTuple("js_media")

urlpatterns += patterns('',
    get_static_url(img_theme_tuple[0],img_theme_tuple[1]),
    get_static_url(css_theme_tuple[0],css_theme_tuple[1]),
    get_static_url(js_theme_tuple[0],js_theme_tuple[1]),
)
