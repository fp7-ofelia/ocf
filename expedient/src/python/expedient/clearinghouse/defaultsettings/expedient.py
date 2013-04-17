'''Expedient-specific settings.

Created on Aug 19, 2010

@author: jnaous
'''
from utils import append_to_local_setting

#VT_AM
##BASIC_AUTH_URLS = [
##    r'^/dummyom/.*',
#    #r'^/xmlrpc/vt_am/.*'
#    r'^/vt_plugin/xmlrpc/vt_am.*'
##]

'''List of URL regular expressions that accept HTTP Basic Authentication.

This is used to enable some tests to work.

'''
##append_to_local_setting("BASIC_AUTH_URLS", BASIC_AUTH_URLS, globals())

SITE_LOCKDOWN_EXCEPTIONS = [
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
    r'^/admin/.*',
    r'^/accounts/password/reset/.*$',
    r'^/img/.*',
    r'^/css/.*',
#    r'^/static/media/.*',
#    r'.*/xmlrpc/?',
]
'''List of URL regular expressions that do not require the user to
be logged in to access.'''
append_to_local_setting(
    "SITE_LOCKDOWN_EXCEPTIONS",
    SITE_LOCKDOWN_EXCEPTIONS,
    globals(),
)

UI_PLUGINS = [
#    ('expedient.ui.html.plugin', 'html_ui', 'expedient.ui.html.urls'),
    ('expedient.ui.rspec.plugin', 'rspec_mgr', 'expedient.ui.rspec.urls'),
]
'''List of UI plugins that are enabled in Expedient.

This is a list of 3-tuples:

    1. The first element is the absolute path to a callable that describes
        the plugin. It should take as input an
        L{expedient.clearinghouse.slice.models.Slice} instance and return a
        tuple (plugin name, plugin description, url to go to for access)
       
    2. The second element is the prefix that is prepended to all urls for
        accessing the plugin. This should be unique across all plugins and
        applications.
       
    3. The third element is the absolute path to the module that should be
        included in URLConf and that contains all the plugin's URLs.

'''
append_to_local_setting("UI_PLUGINS", UI_PLUGINS, globals())

# Installed Aggregate Models [leave variable here to avoid problems]
AGGREGATE_PLUGINS = [
#    ('openflow.plugin.models.OpenFlowAggregate', "openflow", "openflow.plugin.urls"),
##    ('expedient_geni.planetlab.models.PlanetLabAggregate', "planetlab", "expedient_geni.planetlab.urls"),
##    ('expedient_geni.gopenflow.models.GCFOpenFlowAggregate', "gopenflow", "expedient_geni.gopenflow.urls"),
#    ('vt_plugin.models.VtPlugin', "vt_plugin","vt_plugin.urls"),
]
'''List of aggregate plugins that are enabled in Expedient.

This is a list of 3-tuples:

    1. The first element is the absolute path to the Aggregate class.
       
    2. The second element is the prefix that is prepended to all urls for
       accessing the plugin. This should be unique across all plugins and
       applications.
      
    3. The third element is the absolute path to the module that should be
       included in URLConf and that contains all the plugin's URLs.

'''
append_to_local_setting("AGGREGATE_PLUGINS", AGGREGATE_PLUGINS, globals())

SLICE_EXPIRATION_CHECK_INTERVAL = 3600
'''How often should we check for expired slices?

This indicates how often to check for expired slices and stop
them. The given time is in seconds
The accuracy will depend on how often the expedient cron job runs.

'''

SLICE_EXPIRATION_NOTIFICATION_TIME = 3600*24
'''How much earlier should we send an email about slices almost expiring?

This indicates when to send emails to slice owners that their slices
are about to expire. Time is in seconds.

The accuracy will depend on how often the expedient cron job runs.

'''

MAX_SLICE_LIFE = 30
'''Maximum life of a slice without renewing in days'''

# What is the scheme to use when sending urls? 
DOMAIN_SCHEME = "https"
'''What domain scheme should be used for absolute URLs?'''

