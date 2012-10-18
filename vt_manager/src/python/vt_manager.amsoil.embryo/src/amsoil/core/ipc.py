from amsoil.core.exception import NoProviderAvailableError
from amsoil.core.ipcproviders.rabbitmq import RabbitMQ

#from amsoil.config import REQUIRED SETTINGS

class IPC(object):
    '''
    IPC provides inter process communication facilities for multi-process enviornments 
    Warning: services (including core services) that MUST use IPC core service.
    '''
   
    #Singleton instance
    __instance = None

    ##TODO: define provider as config
    PROVIDER_NAME="RabbitMQ"

    #Constructor and singleton
    def __init__(self):
       self.__instance = None
       if IPC.PROVIDER_NAME == "RabbitMQ":
            self._provider = RabbitMQ() 
            return
  
       raise NoProviderAvailableError()
 
    @staticmethod 
    def __getInstance():
        if not IPC.__instance:
            IPC.__instance = IPC()
        return IPC.__instance
 
    #Provisioning operations
    @staticmethod 
    def createQueue(qId,persistent=True):
        '''
        Creates a queue between processes, named qId 
        '''     
        IPC.__getInstance()._provider._createQueue(qId,persistent)
    
    @staticmethod 
    def destroyQueue(qId):
        '''
        Destroys a queue named qId 
        '''     
        IPC.__getInstance()._provider._destroyQueue(qId)
    
    #Actions over queue
    @staticmethod
    def send(qId,message, persistent=True):
        '''
        Sends message to qId
        '''     
        IPC.__getInstance()._provider._send(qId,message,persistent)

    @staticmethod
    def registerReceiver(qId,receiverCallback):
        '''
        Registers (subscribes) to receive messages on the queue qId
        '''     
        IPC.__getInstance()._provider._registerReceiver(qId,receiverCallback)

    @staticmethod
    def unregisterReceiver(qId,receiver):
        '''
        Unregisters (unsubscribes) to receive messages from the queue qId
        '''     
        IPC.__getInstance()._provider._unregisterReceiver(qId,receiver)

    @staticmethod
    def getBufferedMessages(qId,message):
        '''
        Received buffered messages from qId
        '''     
        return IPC.__getInstance()._provider._get(qId)

   
