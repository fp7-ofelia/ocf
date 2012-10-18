import abc
from contextlib import contextmanager
from amsoil.core.mutexserviceproviders.mutexserviceprovider import MutexServiceProvider 
from amsoil.core.mutexserviceproviders.singleprocessmutexservice import SingleProcessMutexService
from amsoil.core.mutexserviceproviders.multiprocessmutexservice import MultiProcessMutexService
 
class MutexService(object):
    '''
    MutexService provide mutual exclusion over an identifier.
    It has two providers ThreadedMutexService and ProcessMutexService that have to be used either in a multi-threaded single process or a multi-threaded multi-process aplication
    '''
    __metaclass__ = abc.ABCMeta
    
    #Singleton instance
    __instance = None

    ##TODO: define multi-process or not as config 
    MULTI_PROCESS=False

    #Constructor and singleton
    def __init__(self):
       if MutexService.MULTI_PROCESS == 0:
            self._provider = SingleProcessMutexService()
       else:
            self._provider = MultiProcessMutexService()
       if not isinstance(self._provider,MutexServiceProvider):
            raise TypeError()
 
    @staticmethod 
    def __getInstance():
        if not MutexService.__instance:
            MutexService.__instance = MutexService()
        return MutexService.__instance
     
    #Public interface
    @staticmethod 
    def lock(stringId):
        '''
        Acquires lock over {stringId} scope
        '''     
        MutexService.__getInstance()._provider._lock(stringId)
    
    @staticmethod 
    def unlock(stringId):
        '''
        Releases lock over {stringId} scope
        '''     
        MutexService.__getInstance()._provider._unlock(stringId)

    #Context Manager stuff (getting smart)
    @staticmethod
    @contextmanager
    def mutex(stringId):
        try:
            yield MutexService.lock(stringId)
        finally:
            MutexService.unlock(stringId)
