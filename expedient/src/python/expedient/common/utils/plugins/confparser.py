"""
Parses the settings configuration file for the given
plugin and returns a dictionary with all the data.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

from utils import join_paths
import ast
import ConfigParser

class ConfParser():

    from settings import SRC_DIR
    # Note: surround inside list whenever treated as a unit
    plugins_path = join_paths([SRC_DIR, "python", "plugins"])

    @staticmethod
    def parse_config(plugin_name, path="./settings.conf"):
        """
        Reads and parses every setting defined in the 'settings.conf' within
        the plugin that goes under the name 'plugin_name'.
        """
        ConfParser.plugin_name = plugin_name
        settings = {}
        try:
            confparser = ConfigParser.RawConfigParser()
            confparser.readfp(open(path))
            for section in confparser.sections():
                settings[section] = {}
                for (key,val) in confparser.items(section):
                    # Any Python structure inside a string is to be converted into the desired structure
                    settings[section][key] = ast.literal_eval(val)
                    # Postprocessing: complete content folders with each plugin absolute path (keeps a copy previously)
                    if section == "paths":
                        settings[section]["relative__%s" % key] = settings[section][key]
                        settings[section][key] = ConfParser.parse_path(plugin_name, settings[section][key])
        except Exception as e:
            print "[WARNING] Exception parsing configuration file '%s'. Details: %s" % (str(path), str(e))
        return settings

    @staticmethod
    def parse_path(plugin_name, plugin_path):
        """
        Transforms the plugin path (along with the plugin name) into an
        absolute URL, taking into account the location of the plugin folders.
        """ 
        try:
            plugin_path = join_paths([[ConfParser.plugins_path], plugin_name, plugin_path])
        except Exception as e:
            print "[WARNING] Exception parsing settings from section 'paths'. Details: %s" % str(e)
        return plugin_path

