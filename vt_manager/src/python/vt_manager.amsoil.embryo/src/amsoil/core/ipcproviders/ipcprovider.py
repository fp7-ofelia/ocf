import abc

class IPCProvider(object):
    '''
    IPCProvider is the API to be implemented for IPCs and used for IPC core class 
    '''
    __metaclass__ = abc.ABCMeta
 
    #Provisioning operations
    @abc.abstractmethod
    def _createQueue(qId,persistent):
        pass
 
    @abc.abstractmethod
    def _destroyQueue(qId):
        pass
 
    #Actions over the queue
    @abc.abstractmethod
    def _send(qId,message,persistent):
        pass

    @abc.abstractmethod
    def _registerReceiver(qId,receiverCallback):
        pass

    @abc.abstractmethod
    def _unregisterReceiver(qId,receiver):
        pass 

    @abc.abstractmethod
    def _getBufferedMessages(qId,message):
        pass 

   
