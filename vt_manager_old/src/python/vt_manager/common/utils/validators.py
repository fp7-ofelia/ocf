'''
Created on Jul 17, 2010

@author: jnaous
'''
import re
from django.core.validators import RegexValidator

mac_re = re.compile(r'^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$')
validate_mac_address = RegexValidator(mac_re, u'Enter a valid MAC address (in "xx:xx:xx:xx:xx:xx" format).', 'invalid')
