"""
Loads plugin settings in Expedient environment.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

from utils import append_to_local_setting
import os
import sys

# Enable imports under this folder
sys.path.append("/opt/ofelia/expedient/src/python/expedient/")
# Import Django environment variables to be used inside PluginLoader class
os.environ['DJANGO_SETTINGS_MODULE'] = "expedient.clearinghouse.settings"
#from plugins.pluginloader import PluginLoader as PLUGIN_LOADER
from common.utils.plugins.pluginloader import PluginLoader as PLUGIN_LOADER
from common.utils.plugins.topologygenerator import TopologyGenerator as TOPOLOGY_GENERATOR

PLUGIN_LOADER.set_plugins_path("/opt/ofelia/expedient/src/python/plugins/")
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
                # 1st: check inside locals
                try:
                    locals()[setting.upper()]
                # 2nd: some vars are already set inside settings (e.g. INSTALLED_APPS)
                # Seek these if previous failed
                except:
                    #exec("from settings import %s" % str(setting.upper()))
                    tmp = __import__('settings', globals(), locals(), [setting.upper()], 0)
                    locals()[setting.upper()] = getattr(tmp, setting.upper())
            except:
                # Setting does not exist in locals() => create it
                try:
                    locals()[setting.upper()] = []
                except Exception as e:
                    print "[Warning] Problem loading setting '%s'. Details: %s" % (str(setting.upper()), str(e))

            if setting.upper() in locals():
                if isinstance(setting_value, list):
                    for value in setting_value:
                        locals()[setting.upper()].append(value)
                else:
                    locals()[setting.upper()].append(setting_value)

