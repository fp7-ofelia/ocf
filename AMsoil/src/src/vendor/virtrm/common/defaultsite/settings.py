'''
Settings for defaultsite

Created on 24 Feb 2010

@author: oppianmatt
'''

from django.conf import settings
import socket

# site id to lookup in the sites app, defaults to 1
SITE_ID = getattr(settings, "SITE_ID", 1)

# domain name to use, defaults socket.get_host_name
SITE_DOMAIN = getattr(settings, "SITE_DOMAIN", socket.gethostname())

# display name for site, defaults to 'defaultsite'
SITE_NAME = getattr(settings, "SITE_NAME", 'defaultsite')