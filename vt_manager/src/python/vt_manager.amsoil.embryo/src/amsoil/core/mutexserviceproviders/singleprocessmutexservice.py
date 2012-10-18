from threading import Lock
from amsoil.core.mutexserviceproviders.mutexserviceprovider import MutexServiceProvider

class SingleProcessMutexService(MutexServiceProvider):
    def __init__(self):
        self.__mutex = Lock()
        self.__mutexStore = dict()
     
    def _lock(self, stringId):
        with self.__mutex:
            if stringId not in self.__mutexStore:
                self.__mutexStore[stringId] = Lock()
            self.__mutexStore[stringId].acquire()
    
    def _unlock(self,stringId):
        #TODO: no garbage collection on Lock {stringId} instances is in implemented yet 
        if self.__mutexStore[stringId]:
            self.__mutexStore[stringId].release()
            
