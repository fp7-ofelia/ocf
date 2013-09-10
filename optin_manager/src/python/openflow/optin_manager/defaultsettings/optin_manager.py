'''
Created on Sep 2, 2010

@author: Peyman Kazemian
'''

BASIC_AUTH_URLS = (
    r'^/xmlrpc/xmlrpc.*',
    ### for testing
    r'^/dummyfv/.*',
)

# List of locations that do not need authentication to access.
SITE_LOCKDOWN_EXCEPTIONS = (
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
    r'^/admin/.*',
    r'^/accounts/password/reset/.*$',
    r'^/img/.*',
    r'^/css/.*',
    r'^/static/media/.*',
    r'^/xmlrpc/sfa/$',
)

DOMAIN_SCHEME = "https"
'''What domain scheme should be used for absolute URLs?'''
