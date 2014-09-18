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
    from settings import SRC_DIR
    # Note: surround inside list whenever treated as a unit
    plugins_path = join_paths([SRC_DIR, "python", "plugins"])

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

        # 'plugins_path' already setted before but just checking
        # for format since that is very important
        default_plugins_path = PluginLoader.plugins_path
        if default_plugins_path[0] == "/":
            default_plugins_path = default_plugins_path[1:]
        if default_plugins_path[-1] == "/":
            default_plugins_path = default_plugins_path[:-1]

        for plugin in PluginLoader.plugin_settings:
            for url_type in ["img", "css", "js"]:
                content_route = PluginLoader.plugin_settings.get(plugin).get("paths").get("relative__%s_dirs" % url_type)
                urlpatterns += patterns('',
#                    url(r'^%s%s/%s/(?P<path>.*)$' % (str(plugin), media_url, url_type),
                    url(r'^%s%s/%s/(?P<path>.*)$' % (str(plugin), media_url, content_route),
                    'django.views.static.serve',
#                    {'document_root': "/%s%s%s/%s" % (PluginLoader.plugins_path, str(plugin), media_url, url_type)}, name="%s_media_%s" % (url_type, str(plugin)))
                    {'document_root': "/%s/%s/%s" % (default_plugins_path, str(plugin), content_route)}, name="%s_media_%s" % (url_type, str(plugin)))
                )
        return urlpatterns

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

    @staticmethod
    def set_plugins_path(plugins_path):
        """
        Sets the folder where plugins are contained.
        """
        PluginLoader.plugins_path = plugins_path

