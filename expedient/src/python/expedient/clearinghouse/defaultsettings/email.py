'''Default Email settings

Created on Aug 18, 2010

@author: jnaous
'''

# See the Django email settings in the Django documentation
# for more information

#SMTP configuration for IM notifications
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'i2catopenflow@gmail.com'
EMAIL_HOST_PASSWORD = 'expedient'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@fp7-ofelia.eu'
EMAIL_SUBJECT_PREFIX = '[OFELIA CF] '

