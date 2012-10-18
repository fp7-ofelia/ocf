import random
from threading import Lock

from amsoil.core import serviceinterface

from ar.adapterbase import AdapterBase
from ar.exceptions import *

class AdapterRegistry(object):
    """
    TODO document all methods
    """
    def __init__(self): 
        self._adapters=list()
        self._mutex=Lock()

    @serviceinterface
    def register(self, adapter):
        if not isinstance(adapter, AdapterBase):
            raise TypeError()
        with self._mutex:
           if adapter in self._adapters:
                raise AlreadyRegisteredError()
           self._adapters.append(adapter) 

    @serviceinterface
    def deregister(self, adapter):
        with self._mutex:
           if adapter not in self._adapters:
                raise NotRegisteredError() 
           self._adapters.remove(adapter) 
            
    @serviceinterface
    def getAdapters(self, filterBy=None):
        if filterBy == None:
            return self._adapters

        with self._mutex:
            result = list()
            for adapter in self._adapters:
                if adapter.supportsType(filterBy):
                    result.append(adapter) 
            return result

    
