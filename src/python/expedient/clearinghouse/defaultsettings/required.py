'''List of required settings.

Created on Aug 19, 2010

@author: jnaous
'''

REQUIRED_SETTINGS = [
    ("admins", ["ADMINS", "MANAGERS"]),
    ("email", ["EMAIL_HOST", "DEFAULT_FROM_EMAIL"]),
    ("gcf", ["GCF_URN_PREFIX"]),
    ("site", ["SITE_DOMAIN"]),
    ("openflow", ["OPENFLOW_GAPI_RSC_URN_PREFIX", "OPENFLOW_GAPI_AM_URN"]),
    ("openflowtests", ["SITE_IP_ADDR", "MININET_VMS"]),
]
'''Required settings that should be overridden for each deployment.

This is a list of tuples
(name of defaultsettings module, list of required settings)

'''
