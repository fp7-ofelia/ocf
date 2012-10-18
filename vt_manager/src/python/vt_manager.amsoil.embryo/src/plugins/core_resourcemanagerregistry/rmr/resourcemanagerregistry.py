import random
from threading import Lock

from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('ResourceManagerRegistry')

from rmr.exception import *
from rmr.resourcemanagerbase import ResourceManagerBase

class ResourceManagerRegistry(object):
    '''Implementation ResourceManagerRegistry API
    
    TODO document all methods
    '''
   
    def __init__(self): 
        self._managers=list()
        self._mutex=Lock()

    @serviceinterface
    def register(self, resourceManager):
        if not isinstance(resourceManager, ResourceManagerBase):
            raise TypeError() 
        with self._mutex:
           if resourceManager in self._managers:
                raise AlreadyRegisteredError()
           self._managers.append(resourceManager) 

    @serviceinterface
    def deregister(self, resourceManager):
        with self._mutex:
           if not resourceManager in self._managers:
                raise NotRegisteredError() 
           self._managers.remove(resourceManager) 
            
    @serviceinterface
    def getManagers(self, filterBy=None):
        if filterBy == None:
            return self._managers

        with self._mutex:
            result = list()
            for rm in self._managers:
                if rm.supportsResourceType(filterBy):
                    result.append(rm) 
            return result

    
    @serviceinterface
    def getRandomManager(self, filterBy=None):
        if (len(self._managers) == 0):
            raise NoResourceManagerForGivenType(filterBy.__class__.__name__)

        if filterBy == None:
            return self._managers[random.randint(0, len(self._managers)-1)]

        with self._mutex:
            supportedManagers = list()
            for rm in self._managers:
                if rm.supportsResourceType(filterBy):
                    supportedManagers.append(rm)
            if (len(supportedManagers) == 0):
                raise NoResourceManagerForGivenType(filterBy.__class__.__name__)
            if (len(supportedManagers) > 1):
                logger.info("Choosing randomly from resource managers (%s)." % (', '.join([rm.__class__.__name__ for rm in supportedManagers]),))
            return supportedManagers[random.randint(0, len(supportedManagers)-1)]



