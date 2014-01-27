'''
	@author: msune

	Ofelia XEN Agent settings loader 
'''

#Import static settings
from vt_manager.settings.staticSettings import *

#Import user settings
from vt_manager.mySettings import *

#Must be here 

ADMINS = [
    ("expedient", ROOT_EMAIL),
]

MANAGERS = ADMINS

#from vt_manager.utils.ThemeManager import initialize


