"""
Loads plugin settings in Expedient.
This is done dynamically, after the normal settings have been loaded
in expedient.clearinghouse.settings -- and thus implicitly added to 
the django.conf.settings abstraction. The latter contains inmmutable 
settings, which are overwritten in this loop with the plug-ins values.

@date: Feb 20, 2013
@author: CarolinaFernandez, lbergesio
"""

import os
import sys
config = __import__('django.conf')
settings = config.conf.settings

#XXX lbergesio:This is ugly and prints before say sys.path and environment are right.
#XXX Try to remove this lines.

# Enable imports under this folder
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
# Import Django environment variables to be used inside PluginLoader class
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"


# Set path for plugins (set at 'expedient/common/utils/plugins/pluginloader.py')
PLUGINS_PATH = os.path.join(settings.SRC_DIR,"python","plugins")
#sys.path.append(PLUGIN_LOADER.plugins_path)
sys.path.append(os.path.join(PLUGINS_PATH))

# Ugly hack to add a number of settinsg (e.g. "INSTALLED_APPS", "AGGREGATE_PLUGINS"
# to the settings even when OCF is loaded via manage.py (remember that settings
# will only load now when urls.py is loaded)

import ast
import ConfigParser

confparser = ConfigParser.RawConfigParser()
settings_to_load = ["installed_apps", "aggregate_plugins"]

for plugin_name in os.listdir(PLUGINS_PATH):
    if os.path.isdir(os.path.join(PLUGINS_PATH, plugin_name)):
        confparser.readfp(open(os.path.join(PLUGINS_PATH, plugin_name, "settings.conf")))
        if confparser.has_section("general"):
            for setting_to_load in settings_to_load:
                conf_setting = list()
                if hasattr(settings, setting_to_load.upper()):
                    conf_setting = getattr(settings, setting_to_load.upper()) or conf_setting
                try:
                    plugin_setting = ast.literal_eval(confparser.get("general", setting_to_load))
                    # Users may set one app only and not wrap this into a list. Wrap it here
                    if not isinstance(plugin_setting, list):
                        plugin_setting = [ plugin_setting ]
                    # If no setting for plugins has been set in INSTALLED_APPS, add these now
                    if [ p for p in plugin_setting if p not in conf_setting ]:
                        setattr(settings, setting_to_load.upper(), conf_setting + plugin_setting)
                except:
                    pass

