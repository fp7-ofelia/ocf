'''
@author: jnaous
'''
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template


''' Theme Management '''

from expedient.common.utils.ExpedientThemeManager import ExpedientThemeManager
ExpedientThemeManager.initialize()

""" Plugin system """
from expedient.common.utils.plugins.pluginloader import PluginLoader as PLUGIN_LOADER
from expedient.common.utils.plugins.topologygenerator import TopologyGenerator as TOPOLOGY_GENERATOR

if not PLUGIN_LOADER.plugin_settings:
    PLUGIN_SETTINGS = PLUGIN_LOADER.load_settings()
    # Iterate over loaded settings to add them to the locals() namespace
    for (plugin, plugin_settings) in PLUGIN_SETTINGS.iteritems():
        for (section, section_settings) in plugin_settings.iteritems():
            for (setting, setting_value) in section_settings.iteritems():
                if hasattr(settings, setting.upper()):
                    conf_setting = getattr(settings, setting.upper())
                else:
#                    setattr(settings, setting.upper(), list()) 
#                    conf_setting = getattr(settings, setting.upper())
                    conf_setting = list()
                try:
                    if not isinstance(setting_value, list):
                        setting_value = [setting_value]
                    if setting_value != conf_setting and setting_value not in conf_setting:
                        conf_setting += setting_value

                except Exception as e:
                    print "[WARNING] Problem loading setting '%s' inside urls.py. Details: %s" % (setting.upper(), str(e))

# This *must* be an absolute path in order for static content to be loaded
#PLUGIN_LOADER.set_plugins_path("/opt/ofelia/expedient/src/python/plugins/")

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'expedient.clearinghouse.views.home', name='home'),

#    url(r'^help/$',
#        direct_to_template,
#        {'template': 'help/index.html'},
#        name='help'),

#    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '../../static/default/img/favicon.ico'}),

    (r'^administration/', include('expedient.clearinghouse.administration.urls')),         
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
    (r'^help/',include('expedient.clearinghouse.help.urls')),
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

try:
    # URLs for static content in plugins
    urlpatterns += PLUGIN_LOADER.generate_static_content_urls(settings.MEDIA_URL)
except Exception as e:
    print "[ERROR] Problem adding URLs for plugins inside expedient.clearinghouse.urls. Details: %s" % str(e)

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

