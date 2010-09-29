'''Expedient-specific settings.

Created on Aug 19, 2010

@author: jnaous
'''

BASIC_AUTH_URLS = (
    r'^/dummyom/.*',
)
'''List of URL regular expressions that accept HTTP Basic Authentication.

This is used to enable some tests to work.

'''

SITE_LOCKDOWN_EXCEPTIONS = (
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
    r'^/admin/.*',
    r'^/accounts/password/reset/.*$',
    r'^/img/.*',
    r'^/css/.*',
    r'^/static/media/.*',
    r'.*/xmlrpc/?',
)
'''List of URL regular expressions that do not require the user to
be logged in to access.'''

UI_PLUGINS = (
    ('expedient.ui.html.plugin', 'html_ui', 'expedient.ui.html.urls'),
)
'''List of UI plugins that are enabled in Expedient.

This is a list of 3-tuples:

    #. The first element is the absolute path to a callable the describes
       the plugin. It should take as input an
       L{expedient.clearinghouse.slice.models.Slice} instance and return a
       tuple (plugin name, plugin description, url to go to for access)
       
    #. The second element is the prefix that is prepended to all urls for
       accessing the plugin. This should be unique across all plugins and
       applications.
       
    #. The third element is the absolute path to the file that should be
       included in URLConf and that contains all the plugin's URLs.

'''

# Installed Aggregate Models
AGGREGATE_PLUGINS = (
    'openflow.plugin.models.OpenFlowAggregate',
    'expedient_geni.planetlab.models.PlanetLabAggregate',
)
'''List of aggregate plugins that are enabled in Expedient.

This is a list of the absolute paths to the plugin's Aggregate class.

'''

# What is the scheme to use when sending urls? 
DOMAIN_SCHEME = "https"
'''What domain scheme should be used for absolute URLs?'''

