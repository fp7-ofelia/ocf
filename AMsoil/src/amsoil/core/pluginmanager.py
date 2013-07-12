"""
The pluginmanager is the core of AMsoil.
The module is responsible for bootstrapping all plugins.

Services
The pluginmanager provides a service registry for plugins. Each plugin can register services on setup.
These services are references to e.g. objects, classes, dicts and even python modules via the registerService(...) method.
Other plugins can retrieve these services via calling getService(...).
Currently, the actual setup of AMsoil may only include only one plugin which defines a certain service.
In other word there may not be two plugins which register a service called the same.

Plugin requirements
Each plugin need a manifest (see below) and a module called plugin at root level.

Plugin Setup
After resolving the dependencies (determined by the manifest) of the plugin, the setup() method of the plugin module is called.
This would be a good place to register the plugin's services.

Manifests
Each plugin in the plugins directory requires a file named "MANIFEST.json".
This json file may specify the following keys in its dictionary (relevant to the pluginmanager):
    "implements" a list of names of services the plugin will register
    "loads-after" a list of names of services which need to be available when the plugin is loaded
    "requires" a list of names of services which the plugin will use, but which do not need to available on the plugin's setup
Example:
    "implements" : ["authorization"],
    "loads-after" : ["config"],
    "requires" : ["policy"],
    "multi-process-supported" : false
    
    (The last line is optional)
    -> The plugin needs the config service when its setup() method is called.
    -> It will register the service authorization and somewhere in its code it will use the policy service.
"""


from __future__ import absolute_import
import sys
import traceback
import os, os.path
import json
import imp

from amsoil import config
from amsoil.core.exception import CoreException

import amsoil.core.log
logger=amsoil.core.log.getLogger('pluginmanager')

class PluginException(CoreException):
    def __init__(self, name):
        super(CoreException, self).__init__()
        self._name = name
    
    def __str__(self):
        return self._name + " (try looking at the log)"

class PluginBootstrapModuleNotLoaded(PluginException):
    pass
class PluginBootstrapSetupMethodNotFoundError(PluginException):
    pass
class PluginManifestNotFoundError(PluginException):
    pass
class PluginMalformedManifestError(PluginException):
    """Something went wrong when parsing the manifest file or the manifest file is missing required keys."""
    pass
class PluginDuplicateServiceDefinitionsInManifestError(PluginException):
    """Two plugins define services which are named the same. This should not be happening."""
    pass
class PluginLoadAfterResolvingError(PluginException):
    """The dependencies given by loads-after can not be satisfied."""
    pass
class PluginRequiresCanNotBeFulfilledError(PluginException):
    """The dependencies given by requires can not be satisfied. The requires plugin is probably not present."""
    pass
class PluginUnsupportedMultiprocess(PluginException):
    """The current environment requires multiprocess support (set by in the config file) but the plugin does not support it."""
    pass
class ServiceAlreadyRegisteredError(PluginException):
    """The service which was was attempted to be registered has been registered before."""
    pass
class ServiceNotRegisteredError(PluginException):
    """The service the caller asked for has not been registered. 
    If you run into this exception, please check if you specified sufficient requires in the manifest"""
    pass
class ServiceNameNotFoundInManifestError(PluginException):
    """The plugin tries to register a service which has not been specified in the implements section in the manifest."""
    pass

_pluginList = []
_serviceRegistry = {}
_currentSetupPluginInfo = None # in order to avoid passing pluginInfos to the setup methods of plugins, we remember
# a reference to the current pluginInfo during the plugin setup. If there is not setup method being called this variable should be None.
# This is a pure convenience for the plugin-developer, so he does not have to pass the pluginInfo back to registerService
# (registerService needs info from the PluginInfo so it can validate the user's parameters).

MANIFEST_FILENAME='MANIFEST.json'
IMPLEMENTS_KEY='implements'
LOADS_AFTER_KEY='loads-after'
MULTIPROCESS_SUPPORTED_KEY="multi-process-supported"

REQUIRES_KEY='requires'
BOOTSTRAP_MODULE_NAME='plugin'

class PluginInfo(object):
    """
    Data holder for the _pluginList.
    This class handles one plugin's data and the setup/loading of a plugin.
    serviceNames **and** dependencies are service names. They are arbitrary and do not necessarly need correspond to the plugin's name.
    """
    def __init__(self, pluginPath, manifest):
        """
        Receives the path of the plugin, service names provided by the plugin and a list of dependencies.
        """
        # we could check the format of serviceNames and dependencies here, but I dont yet
        try:
            self._pluginPath = pluginPath
            self._serviceNames = manifest[IMPLEMENTS_KEY]
            self._loadsAfter = manifest[LOADS_AFTER_KEY]
            self._requires = manifest[REQUIRES_KEY]
            if (MULTIPROCESS_SUPPORTED_KEY in manifest):
                self._supports_multiprocess = manifest[MULTIPROCESS_SUPPORTED_KEY]
            else:
                self._supports_multiprocess = True
        except KeyError, e:
            raise PluginMalformedManifestError(path)
            
        self._pluginModule = None

    def setup(self):
        """Load the plugin, set the _pluginModule and call the setup method."""
        logger.info("loading %s" % self.pluginName)
        try:
            bFile, bFilename, bDesc = imp.find_module(BOOTSTRAP_MODULE_NAME, [self._pluginPath])
            sys.path.append(os.path.dirname(bFilename))
            self._pluginModule = imp.load_module(self.pluginName, bFile, bFilename, bDesc)
        except ImportError, e:
            logger.exception(traceback.format_exc())
            raise PluginBootstrapModuleNotLoaded(self.pluginName)
        global _currentSetupPluginInfo # see documentation above
        if not hasattr(self._pluginModule, 'setup'):
            self._pluginModule = None
            raise PluginBootstrapSetupMethodNotFoundError(self.pluginName)
        _currentSetupPluginInfo = self
        self._pluginModule.setup()
        _currentSetupPluginInfo = None

    def implementsService(self, name):
        """Tells if the plugin's manifest specifies the service's name given."""
        return (name in self._serviceNames)

    def allLoadsAfterSatisfied(self, pluginList):
        """
        Checks if all plugins specified in _loadsAfter have been loaded.
        """
        for depServiceName in self._loadsAfter:
            # find out if all dependent service names have already been loaded, if not return False
            foundService = False
            for otherPluginInfo in pluginList:
                if otherPluginInfo.implementsService(depServiceName):
                    foundService=True
                    if not otherPluginInfo.loaded: # here I assume that service names are unique
                        return False
                    break
            if not foundService:
                return False
        return True

    def allRequiresSatisfied(self, pluginList):
        """
        Checks if all plugins specified in _requires are available.
        """
        for depServiceName in self._requires: # this is a little redundant to above
            foundService=False
            for otherPluginInfo in pluginList:
                if otherPluginInfo.implementsService(depServiceName):
                    foundService=True
                    break
            if not foundService:
                return False
        return True

    @property
    def loaded(self):
        return self._pluginModule != None
    
    @property
    def supports_multiprocess(self):
        return self._supports_multiprocess

    @property
    def serviceNames(self):
        return set(self._serviceNames)
    
    @property
    def pluginModule(self):
        return self._pluginModule
    
    @property
    def pluginName(self):
        return os.path.basename(self._pluginPath)


def init(pluginsPath):
    """
    Should be called during bootstrapping of the AM.
    Walks through the plugins directory and reads the dependencies (loadsAfter, requires) and saves this information to the pluginList.
    Then the plugins' setup method is called, where the plugin can register it's services.
    The order of loading depends on the loadsAfter tree.
    
    Semantics:
    During the setup of the plugins the plugins can assume that the service which are specified in loadsAfter are present.
    The plugins which are specified in requries are not necessarily present during the setup call, but the system enforces
    that they are present in the system after all plugins are present.
    """
    for path in os.listdir(pluginsPath):
        absPath = os.path.join(pluginsPath, path)
        if not os.path.isdir(absPath):
            continue
        try:
            manifestFile = open(os.path.join(absPath, MANIFEST_FILENAME), 'r')
        except IOError, e: # handle error if manifest does not exist
            raise PluginManifestNotFoundError(path)
        try:
            manifest = json.load(manifestFile)
        except Exception, e:
            raise PluginMalformedManifestError(path)
        _pluginList.append(PluginInfo(absPath, manifest))

    # check for duplications of service implementations
    allServices = []  # damn i can not find decent documentation on sets... the next couple of lines are ugly
    for pluginInfo in _pluginList:
        allServices.extend(pluginInfo.serviceNames)
    for s in set(allServices):
        allServices.remove(s)
    if len(allServices) > 0:
        raise PluginDuplicateServiceDefinitionsInManifestError(', '.join(allServices))
    
    if config.IS_MULTIPROCESS:
        for pluginInfo in _pluginList:
            if not pluginInfo.supports_multiprocess:
                raise PluginUnsupportedMultiprocess(pluginInfo.pluginName)
    
    # Load the plugins in according to the loadsAfter specifications in the plugin's manifest.
    # This is how it works:
    #   iterate through the pluginList and load the plugins which have no (loadsAfter) dependencies
    #   repeat this iteration as long as at least one plugin was loaded in the last cycle.
    #   if there are unloaded plugins left after that, there is an unsatifyable dependency (either cycle or undefined service names).
    loadedPlugin = True
    while (loadedPlugin):
        loadedPlugin = False
        for pluginInfo in _pluginList:
            if pluginInfo.loaded:
                continue
            if pluginInfo.allLoadsAfterSatisfied(_pluginList):
               pluginInfo.setup()
               loadedPlugin = True
    
    # crash if not all plugins loaded
    # also crash if not all requires statements are satisfied
    for pluginInfo in _pluginList:
        if not pluginInfo.loaded:
            raise PluginLoadAfterResolvingError(pluginInfo.pluginName)
        if not pluginInfo.allRequiresSatisfied(_pluginList):
            raise PluginRequiresCanNotBeFulfilledError(pluginInfo.pluginName)
    logger.info("done loading plugins")

def getService(name):
    """
    Receives the thing (object, module or whatever) which has been added by the registerService.
    """
    if not name in _serviceRegistry:
        raise ServiceNotRegisteredError(name)
    return _serviceRegistry[name]
    
def registerService(name, service):
    """
    Register a service under the given name
    Service can be an object, a class or any other thing (even a module or a package)
    """
    logger.info("registering service %s" % name)
    if name in _serviceRegistry: # check if the service has already been registered
        raise ServiceAlreadyRegisteredError(name)

    # to avoid developer's misspelling: check if the service's name is in the manifest file
    if (_currentSetupPluginInfo) and (not _currentSetupPluginInfo.implementsService(name)):
        raise ServiceNameNotFoundInManifestError(name)
    _serviceRegistry[name] = service

