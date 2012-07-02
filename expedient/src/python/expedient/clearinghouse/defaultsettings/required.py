'''List of required settings.

Created on Aug 19, 2010

@author: jnaous
'''

REQUIRED_SETTINGS = [
    ("admins", ["ADMINS", "MANAGERS"]),
#    ("email", ["EMAIL_HOST", "DEFAULT_FROM_EMAIL"]),
#    ("gcf", ["GCF_BASE_NAME"]),
    ("site", ["SITE_DOMAIN"]),
#    ("openflowtests", ["SITE_IP_ADDR", "MININET_VMS"]),
]
'''Required settings that should be overridden for each deployment.

This is a list of tuples
(name of defaultsettings module, list of required settings)

'''
