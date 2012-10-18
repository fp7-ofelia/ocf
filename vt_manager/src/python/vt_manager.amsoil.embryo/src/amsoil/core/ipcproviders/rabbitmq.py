import time 
import pika
import hashlib 
import threading 
from threading import Lock
from amsoil.core.ipcproviders.ipcprovider import IPCProvider
from amsoil.core.ipcproviders.exception import QueueAlreadyDeclared, QueueDoesNotExist, CallbackAlreadyRegistered, InvalidCallback 
import amsoil.core.log
from amsoil.config import IPC_RABBITMQ_SERVER 

#Handling credentials (if defined)
rabbitMQServerCredentials = None

try:
    from amsoil.config import IPC_RABBITMQ_USERNAME, IPC_RABBITMQ_PASSWORD
    rabbitMQServerCredentials = pika.PlainCredentials(IPC_RABBITMQ_USERNAME, IPC_RABBITMQ_PASSWORD)
except ImportError:
    IPC_RABBITMQ_USERNAME = None
    IPC_RABBITMQ_PASSWORD = None

#Auxilary stuff
class CallbackHandler(threading.Thread):
    '''
    Thread that handles asynchronous message receiving and calls appropiate callback defined by user
    '''
    def __init__(self, qId, callback):
        threading.Thread.__init__(self)  
        self.logger = amsoil.core.log.getLogger(self.__class__.__name__+":"+qId)
        self.logger.debug("Initializing callback handler for queue:"+qId)

        #initialize RabbitMQ connection
        if IPC_RABBITMQ_USERNAME and IPC_RABBITMQ_PASSWORD:
            credentials = pika.PlainCredentials(IPC_RABBITMQ_USERNAME, IPC_RABBITMQ_PASSWORD)
            
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(IPC_RABBITMQ_SERVER,credentials=rabbitMQServerCredentials))
        self._channel = self.__connection.channel()
        self._callback = callback    
        self.qId = qId 
        self.tag = qId+getattr(callback,'__name__')
 
    def run(self):
        self._channel.basic_consume(self._callback,queue=self.qId,no_ack=True, consumer_tag=self.tag)
        self._channel.start_consuming()

    def destroy(self):
        self.logger.debug("Destroying callback handler for queue:"+self.qId)
        self._channel.basic_cancel(self.tag)
        self.logger.debug("Consuming loop has finished for queue:"+self.qId)
        #self._channel.close() # <--- pika method buggy? https://github.com/celery/kombu/issues/140
        #self.logger.debug("Channel closed for queue:"+self.qId)
        self.__connection.close()
        self.logger.debug("Connection closed for queue:"+self.qId)



#Provider
class RabbitMQ(IPCProvider):
    '''
    RabbitMQ provider is an IPC AMSoil interface compliant provides that uses an external RabbitMQ server. Note that server needs to be setup a priori.
    '''

    def __init__(self):
        self.logger = amsoil.core.log.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing RabbitMQ provider...")

        #initialize RabbitMQ connection
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(IPC_RABBITMQ_SERVER,credentials=rabbitMQServerCredentials))
        self.__ctrlConnection = pika.BlockingConnection(pika.ConnectionParameters(IPC_RABBITMQ_SERVER,credentials=rabbitMQServerCredentials))
        self._channel = self.__connection.channel()
    
        #Internal state
        self._callbackHandlers = dict() #Key: hash value: thread obj.
        self._mutex = Lock()

    def _checkQueueExists(self, qId): 
        try:
            self.__ctrlConnection.channel().queue_declare(queue=qId, passive=True)
        except Exception as e:
            return False 
        
        return True

    #Provisioning operations
    def _createQueue(self,qId,persistent):
        self.logger.debug("Creating queue: "+str(qId))
        
        if self._checkQueueExists(qId):
            raise QueueAlreadyDeclared() 
         
        with self._mutex: #Enough to be managing lock locally
            self._channel.queue_declare(queue=qId, durable=persistent, exclusive=False, auto_delete=False) #, callback)
            #self._queuesInstantiated.append(qId) 
       
        self.logger.debug("Queue created:"+qId) 
        #self.logger.debug("Queue list "+str(self._queuesInstantiated))
        
    def _destroyQueue(self,qId):
        self.logger.debug("Destroying queue: "+str(qId))

        if not self._checkQueueExists(qId):
            raise QueueDoesNotExist() 
 
        with self._mutex: #Enough to be managing lock locally
            self._channel.queue_delete(queue=qId) 
            #self._queuesInstantiated.remove(qId) 
        
        self.logger.debug("Queue destroyed:"+qId) 
        #self.logger.debug("Queue list "+str(self._queuesInstantiated))
    
    #Actions over the queue
    def _send(self,qId,message,persistent):
        self.logger.debug("Sending message to queue: "+str(qId)+" message:"+str(message))
        self._channel.basic_publish(exchange='', routing_key=qId, body=message, mandatory=True, properties=pika.BasicProperties(
                              content_type="text/plain",
                              delivery_mode=1))

    def __generateCallbackHash(self, qId, callback): 
        #Creating unique hash(qId,callback)
        m = hashlib.md5()
        m.update(qId+getattr(callback,'__name__'))
        return m.digest()
 
    def _registerReceiver(self,qId,receiverCallback):
        
        if not hasattr(receiverCallback, '__call__'):
            raise InvalidCallback
        
        hash= self.__generateCallbackHash(qId, receiverCallback)
        
        if hash in self._callbackHandlers:
            raise CallbackAlreadyRegistered
      
        with self._mutex:
            if not self._checkQueueExists(qId):
                raise QueueDoesNotExist()
            
            self.logger.debug("Registering to queue: "+str(qId)) 
            thread = CallbackHandler(qId,receiverCallback) 
            self._callbackHandlers[hash] = thread
            thread.start()
  
    def _unregisterReceiver(self,qId,receiver):
        hash = self.__generateCallbackHash(qId, receiver)
        with self._mutex:
            if hash not in self._callbackHandlers:
                self.logger.warning("Trying to unregistering from queue: "+str(qId)+" an unknown method... Skipping..")
                return 
            self.logger.debug("Unregistering from queue: "+str(qId)) 
            thread=self._callbackHandlers[hash]
            thread.destroy()
             
    def _getBufferedMessages(self,qId,message):
        self.logger.debug("Getting buffered messages from queue: "+str(qId)) 
        raise Exception("not implemented")    
