"""
@author: msune, CarolinaFernandez
Ofelia VT manager settings loader 
"""

# Import static settings
from vt_manager.settings.staticSettings import *

# Import user settings
from vt_manager.mySettings import *

# Load database info
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.%s" % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
    }
}

#Must be here 
ADMINS = [
    ("expedient", ROOT_EMAIL),
]

MANAGERS = ADMINS

#from vt_manager.utils.ThemeManager import initialize


