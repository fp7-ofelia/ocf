"""
Loads plugin settings in Expedient environment.

@date: Feb 20, 2013
@author: CarolinaFernandez, lbergesio
"""

import os
import sys
config=__import__('django.conf')
settings = config.conf.settings

#print sys.path
#print os.environ['DJANGO_SETTINGS_MODULE']

#XXX lbergesio:This is ugly and prints before say sys.path and environment are right.
#XXX Try to remove this lines.

# Enable imports under this folder
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
# Import Django environment variables to be used inside PluginLoader class
os.environ['DJANGO_SETTINGS_MODULE'] = "expedient.clearinghouse.settings"
#from plugins.pluginloader import PluginLoader as PLUGIN_LOADER
from common.utils.plugins.pluginloader import PluginLoader as PLUGIN_LOADER
from common.utils.plugins.topologygenerator import TopologyGenerator as TOPOLOGY_GENERATOR

PLUGIN_LOADER.set_plugins_path(os.path.join(os.path.dirname(__file__), "../../../plugins/"))
PLUGIN_SETTINGS = PLUGIN_LOADER.load_settings()

"""
Assumes that plugin_settings follows the structure
{
    'plugin_name': {
        'section_name': {
            'attribute_name': 'attribute_value',
            ...
        },
        ...
    },
    ...
}
"""
# Iterate over loaded settings to add them to the locals() namespace
for (plugin, plugin_settings) in PLUGIN_SETTINGS.iteritems():
    for (section, section_settings) in plugin_settings.iteritems():
        for (setting, setting_value) in section_settings.iteritems():
            try:
                conf_setting = getattr(settings, setting.upper())
            except Exception as e:
                setattr(settings, setting.upper(), list()) 
                conf_setting = getattr(settings, setting.upper())
            try:
                if not isinstance(setting_value, list):
                    setting_value = [setting_value]
                conf_setting += setting_value
            except Exception as e:
                print "WARNING: Could not load setting : %s" % setting.upper()
                print e

