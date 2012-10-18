from threading import Lock
from amsoil.core.exception import NotImplementedError
from amsoil.core.mutexserviceproviders.mutexserviceprovider import MutexServiceProvider
from amsoil.core.ipc import IPCService

class MultiProcessMutexService(MutexServiceProvider):
    '''
    MultiProcessMutexService is a MutexServiceProvider interface compliant mutex service that uses IPC core service to implement inter-process locks.
    '''

    def __init__(self):
        #Initialization protocol is as follows: 
        #1) Current process attempts to create a non-persistent (across executions) $MUTEX_QUEUE_NAME$ queue
        #2) If QueueAlreadyExists exception is captured, then process is slave otherwise master
        #3) Master process will hold mutex state, while slaves will simply cache it 
        #4) Master - Slave(s) will periodically check for the existance of a Master
        #5) In case MASTER is down, reconfiguration must happen

        self.__master = False
        self.__MUTEX_QUEUE_NAME = "amsoil-dmutex"
        
        #Attempt to create the queue (1)
        try:
            IPCService.createQueue(self.__MUTEX_QUEUE_NAME,persistent=False)
              
    def _lock(self, stringId):
        pass

    def _unlock(self,stringId):
        pass
 
