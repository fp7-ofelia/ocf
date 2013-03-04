"""
Loads settings for every plugin and returns a dictionary with all the data.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

import os 
from confparser import ConfParser
from utils import join_paths, Singleton

class PluginLoader():

    # Allows only one instance of this class
    __metaclass__ = Singleton
    plugin_settings = {}
    from localsettings import SRC_DIR
    # Note: surround inside list whenever treated as a unit
    plugins_path = join_paths([SRC_DIR, "python"])

    @staticmethod
    def generate_static_content_urls(media_url = ""):
        """
        Crafts URLs for static content (img, css, js) inside plugins.
        Note: content inside plugin is expected to follow the same structure as in settings.MEDIA_URL
        (e.g. '/static/media/default'). The generated URLs will have the associated name X_media_Y,
        where X = {"img","css","js"} and Y = (plugin name)
        """
        from django.conf.urls.defaults import patterns, url
        urlpatterns = []
        for plugin in PluginLoader.plugin_settings:
            for url_type in ["img", "css", "js"]:
                urlpatterns += patterns('',
                    url(r'^%s%s/%s/(?P<path>.*)$' % (str(plugin), media_url, url_type),
                    'django.views.static.serve',
                    {'document_root': "/%s%s%s/%s" % (PluginLoader.plugins_path, str(plugin), media_url, url_type)}, name="%s_media_%s" % (url_type, str(plugin)))
                )
        return urlpatterns

    # FIXME: add method to get ID from given plugin.model whose
    # attribute = filter (so, so) and probably use a Foreign Key (if
    # one wants to get all the interfaces connected to a switch, etc)
    @staticmethod
    def get_id_from_element(plugin, model, attribute, filter, foreign_key=None):
        pass

    @staticmethod
    def load_settings(path=None):
        """
        Entry point for the load of settings. If settings were not already defined, load these.
        """
        try:
            pl = PluginLoader()
            # If settings were already loaded, do not attempt again
            if not pl.plugin_settings:
                if not path:
                    path = pl.plugins_path
                else:
                    pl.set_plugins_path(path)
                PluginLoader.plugin_settings = pl.load_settings_from_folder(path)
        except Exception as e:
            print "[WARNING] There may be some problem with the plugin configuration files. Exception: %s" % str(e)
        return PluginLoader.plugin_settings

    def load_settings_from_folder(self, plugins_path="."):
        """
        Iterates over the folders inside the plugins path and loads each
        one's settings in a big dictionary that follows the structure:
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
        try:
            for plugin_name in os.listdir(plugins_path):
                if os.path.isdir(os.path.join(plugins_path, plugin_name)):
                    try:
                        plugin_path = os.path.join(plugins_path, plugin_name)
                        plugin_data = self.load_settings_from_plugin(plugin_path)
                        if plugin_data:
                            self.plugin_settings[plugin_name] = plugin_data
                    except:
                        pass
        except:
            pass
        return self.plugin_settings

    def load_settings_from_plugin(self, path="./"):
        """
        Read the plugin's configuration file into a dictionary where each
        section of the config is a sub-dictionary that contains some properties.
        """
        plugin_name = ""
        # Remove last slash to parse data
        if path[-1] == "/":
            path = path[:-1]
        plugin_name = path.split("/")[-1]
        path = path + "/settings.conf"
        return ConfParser.parse_config(plugin_name, path)

#    @staticmethod
#    def load_ui_data(slice):
#        """
#        Calls the method 'get_ui_data' present in each plugin and mix the data for all
#        plugins in a dictionary with nodes, links and total number of islands. This data
#        will be sent to the topology visor, shown in the slice view.
#        """
#        plugin_ui_data = dict()
#        plugin_ui_data['d3_nodes'] = []
#        plugin_ui_data['d3_links'] = []
#        plugin_ui_data['n_islands'] = 0
#        plugin_ui_data_aux = dict()
#
#        for plugin in PluginLoader.plugin_settings:
#            try:
#                plugin_method = "%s_get_ui_data" % str(plugin)
#                plugin_import = PluginLoader.plugin_settings.get(plugin).get("general").get("get_ui_data_class")
#                # Check that plugin does have a method to get UI data
#                if plugin_import:
#                    #exec(plugin_import)
#                    tmp = __import__(plugin_import, globals(), locals(), ['get_ui_data'], 0)
#                    locals()[plugin_method] = getattr(tmp, 'get_ui_data')
#                    plugin_ui_data_aux = locals()[plugin_method](slice)
#
#                    # Not so happy to need this post-processing after the plugin's data retrieval...
#                    [ plugin_ui_data['d3_nodes'].append(node) for node in plugin_ui_data_aux['nodes'] ]
#                    [ plugin_ui_data['d3_links'].append(link) for link in plugin_ui_data_aux['links'] ]
#                    plugin_ui_data['n_islands'] = plugin_ui_data['n_islands'] + plugin_ui_data_aux['n_islands']
#                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
#            except Exception as e:
#                print "[ERROR] Problem loading UI data inside PluginLoader. Details: %s" % str(e)
#        return plugin_ui_data

    @staticmethod
    def set_plugins_path(plugins_path):
        """
        Sets the folder where plugins are contained.
        """
        PluginLoader.plugins_path = plugins_path

