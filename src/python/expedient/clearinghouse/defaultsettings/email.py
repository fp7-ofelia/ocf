'''Default Email settings

Created on Aug 18, 2010

@author: jnaous
'''

# See the Django email settings in the Django documentation
# for more information
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'clearinghouse.geni@gmail.com'
EMAIL_HOST_PASSWORD = "the password" # example
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@geni.org'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '
