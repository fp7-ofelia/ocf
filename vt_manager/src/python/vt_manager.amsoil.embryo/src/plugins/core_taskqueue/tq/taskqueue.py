import abc
from tq.base.taskqueueprovider import TaskQueueProvider 
from tq.providers.singleprocesstaskqueue import SingleProcessTaskQueue
from tq.providers.multiprocesstaskqueue import MultiProcessTaskQueue
 
class TaskQueue(object):
    '''
    TaskQueue provide mutual exclusion over an identifier.
    It has two providers ThreadedTaskQueue and ProcessTaskQueue that have to be used either in a multi-threaded single process or a multi-threaded multi-process aplication
    '''
    __metaclass__ = abc.ABCMeta
    
    #Singleton instance
    __instance = None

    ##TODO: define multi-process or not as config 
    MULTI_PROCESS=False

    #Constructor and singleton
    def __init__(self):
       if TaskQueue.MULTI_PROCESS == 0:
            self._provider = SingleProcessTaskQueue()
       else:
            self._provider = MultiProcessTaskQueue()
       if not isinstance(self._provider,TaskQueueProvider):
            raise TypeError()
 
    @staticmethod 
    def __getInstance():
        if not TaskQueue.__instance:
            TaskQueue.__instance = TaskQueue()
        return TaskQueue.__instance
     
    #Public interface
    @staticmethod 
    def lock(stringId):
        '''
        Acquires lock over {stringId} scope
        '''     
        TaskQueue.__getInstance()._provider._lock(stringId)
    
    @staticmethod 
    def unlock(stringId):
        '''
        Releases lock over {stringId} scope
        '''     
        TaskQueue.__getInstance()._provider._unlock(stringId)

