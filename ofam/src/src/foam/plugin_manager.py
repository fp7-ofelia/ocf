# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

class PluginManager(object):
  def __init__ (self, plugin_dir):
    self.plugin_root = plugin_dir
    self.__plugins = {}

    self._loadPlugins()

  def _loadPlugins (self):
    pass

  def getByInterface (self, interface):
    for v in self.__plugins.itervalues():
      if v.interfaces("foam.interface.rpc"):
        yield v
