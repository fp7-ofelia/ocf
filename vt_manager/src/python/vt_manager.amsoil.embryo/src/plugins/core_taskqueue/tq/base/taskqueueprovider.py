import abc

class TaskQueueProvider(object):
    '''
    TaskQueueProvider is the API to be implemented for a TaskQueueProvider that TaskQueue requires 
    '''
    __metaclass__ = abc.ABCMeta
    
    #Service implementors API. They *MUST NOT* export the service in its own as public methods 
    @abc.abstractmethod
    def _lock(self, stringId):
        '''
        Acquires lock over {stringId} scope
        '''     
        self._provider.lock(stringId) 
    
    @abc.abstractmethod
    def _unlock(self,stringId):
        '''
        Acquires lock over {stringId} scope
        '''     
        self._provider.unlock(stringId) 

