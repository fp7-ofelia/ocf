'''
Ofelia VT AM settings file (static settings)

@author: msune, CarolinaFernandez
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: VT AM settings
#
# Static settings for Virtual Machine Aggregate Manager.
#

import sys, traceback, logging
from os.path import dirname, join

#
# Email configuration.
#
DEFAULT_FROM_EMAIL = "OFELIA-noreply@fp7-ofelia.eu"
EMAIL_SUBJECT_PREFIX = '[OFELIA CF] '
EMAIL_USE_TLS=True
EMAIL_HOST='mail.eict.fp7-ofelia.eu'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_PORT=25 

#
# Set true to enable debug.
#
DEBUG = True

##
## Advanced parameters.
## You SHOULD NOT change them unless you have a good reason.
##

#
# Directory for the VT manager sources.
#
SRC_DIR = join(dirname(__file__), '../../../')

#
# Database default parameters.
#
DATABASE_ENGINE = 'mysql'
DATABASE_HOST = ''
DATABASE_PORT = ''

#
# Default sitename.
#
SITE_NAME = 'OFELIA CF VT Manager'

#
# Fully qualified name
#
SITE_DOMAIN = 'expedient.site:8445'

