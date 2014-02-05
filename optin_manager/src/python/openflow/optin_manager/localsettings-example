'''
Ofelia Opt-in AM user settings file

@author: msune, CarolinaFernandez, lbergesio
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: Opt-in settings
#
# Basic settings for the Opt-in Manager configuration.
#

#
# Directories for the Opt-in sources and the configuration file.
#
CONF_DIR = '/opt/ofelia/optin_manager/src/python/openflow/optin_manager'
SRC_DIR = '/opt/ofelia/optin_manager/src'

#
# Super user credentials to access the admin GUI.
# aka Island Manager credentials.
#
ROOT_USERNAME = "changeMe"
ROOT_PASSWORD = "changeMe"
ROOT_EMAIL    = "changeMe@gmail.com"

#
# You may add different groups here and decide whether they are
# managers or not.
#
ADMINS = [
    ("expedient", ROOT_EMAIL),
]
MANAGERS = ADMINS

#
# Database parameters.
# DATABASE_NAME: default is "ocf__optin_manager"
# DATABASE_HOST: it is usually 'localhost' (or 127.0.0.1)
#
DATABASE_NAME = "ocf__optin_manager"
DATABASE_USER = "changeMe"
DATABASE_PASSWORD = "changeMe"
DATABASE_HOST = "127.0.0.1"

#
# Name for the island that is to be set on your host.
#
ISLAND_NAME   = "i2CAT"

#
# Address and IP you would like to use for e-mails sent to users and Island Manager.
# SITE_DOMAIN: format is "url[:port]". Do NOT use http[s]:// here.
# 
SITE_DOMAIN = "ocf.mydomain.net:2345"
SITE_IP_ADDR = "192.168.254.193"

#
# VLANS not allowed: when simple OF slices are requested, Optin offers VLAN tags
# in the normal range [1-4095] except for those tags in VLANS_UNALLOWED.
#
UNALLOWED_VLANS = []


##
## Theme Manager 
##

#
# THEME: write a theme_name here to create a theme.
#
# Manually create the theme_name's media directory and the static directories (images,
# css, js) in SRC_DIR/static/openflow/optin_manager/media/theme_name/
# For templates (.html) files add a directory called theme_name in the same
# location as your default TEMPLATES_DIR if needed.
#
# Check https://github.com/fp7-ofelia/ocf/wiki/Theme-Manager-Configuration
# for further information on how to install new themes for OCF.
#
THEME = "default"
