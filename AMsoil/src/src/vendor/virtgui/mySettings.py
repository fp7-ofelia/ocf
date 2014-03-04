'''
Ofelia VT AM User settings file

@author: msune, CarolinaFernandez
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: VT AM settings
#
# User settings for Virtual Machine Aggregate Manager.
#

#
# User management for the Graphical User Interface.
#
ROOT_USERNAME  = "expedient"
ROOT_PASSWORD  = "expedient"
ROOT_EMAIL     = "i2catopenflow@gmail.com"

# 
# XMLRPC access. Set user and password to access the XMLRPC
# methods from Expedient.
#
XMLRPC_USER    = "xml"
XMLRPC_PASS    = "rpc"

#
# Database parameters.
# DATABASE_HOST: it is usually 'localhost' (or 127.0.0.1)
#
DATABASE_NAME = "vt_manager"
DATABASE_USER = "expedient"
DATABASE_PASSWORD = "expedient"
DATABASE_HOST = "127.0.0.1"

#
# Name for the island that is to be set on your host.
#
ISLAND_NAME    = "i2cat"

#
# IP and port you would like to use to access Expedient GUI.
#
VTAM_IP = "192.168.254.200"
VTAM_PORT = "8445"

#
# Agent monitoring interval in seconds. That is, seconds until it
# asks for the current status of the servers and virtual machines.
# MONITORING_INTERVAL: default is 45.
#
##MONITORING_INTERVAL = 45

#
# THEME: write a theme_name here to create a theme.
#
# Create the theme_name's media directory and the static directories (images,
# css, js) in SRC_DIR/python/vt_manager/views/static/media/theme_name/
# For templates (.html) files add a directory called theme_name in the same
# location as your default TEMPLATES_DIR: [networking, policyEngine, users, 
# ...] (check django.py file) in
# SRC_DIR/python/vt_manager/views/templates/theme_name as needed.
#
# Check https://github.com/fp7-ofelia/ocf/wiki/Theme-Manager-Configuration
# for further information on how to install new themes for OCF.
#
THEME = 'default'




### Section 2: E-mail settings
#
# Configure your SMTP parameters.
#

#
# Address of the mailing host.
#
EMAIL_HOST = "mail.eict.fp7-ofelia.eu"

#
# Port used in that host. Default is '25'.
#
EMAIL_PORT = 25

#
# User to authenticate against mailing host.
#
EMAIL_HOST_USER = ''

#
# Password to authenticate against mailing host.
#
EMAIL_HOST_PASSWORD = ''

#
# Activate TLS (True) or SSL (False).
#
EMAIL_USE_TLS = True

#
# Activate TLS (True) or SSL (False).
DEFAULT_FROM_EMAIL = 'no-reply@ofelia-fp7.eu'

#
# Subject (a prefix of it) for the e-mail.
#
EMAIL_SUBJECT_PREFIX = '[OFELIA CF] '
