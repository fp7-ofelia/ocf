'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.core.urlresolvers import reverse

def plugin(slice):
    return ("HTML Table UI", "Shows OpenFlow and PlanetLab resources in the \
slice as a table.", reverse("html_plugin_home", args=[slice.id]))
    
