'''Default Email settings

Created on Aug 18, 2010

@author: jnaous
'''

# See the Django email settings in the Django documentation
# for more information

#SMTP configuration for IM notifications
EMAIL_HOST = "mail.eict.fp7-ofelia.eu"
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'OFELIA_noreply@fp7-ofelia.eu'
EMAIL_SUBJECT_PREFIX = '[OFELIA CF] '

