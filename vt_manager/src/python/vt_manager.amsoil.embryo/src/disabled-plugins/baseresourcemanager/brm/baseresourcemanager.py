import abc
import amsoil.core.pluginmanager as pm
from brm.exception import UnknownDateTimeFormatError, UnknownResourceTypeError

#Load ResourceManager interface from resourcemanagerregsitry plugin
ResourceManager = pm.getService("resourcemanagerregistry.resourcemanagerinterface").ResourceManager
Resource = pm.getService("resourcemanagerregistry.resourceinterface").Resource

##XXX: Config parameters => to use Config API
class BaseResourceManager(ResourceManager):
    '''
    Simple resource Manager wraps simple allocation logic
  
    '''
    #__metaclass__ = abc.ABCMeta

    TEMP_RESERVE_SIGNAL="resource.temporallyreserve"
    RESERVE_SIGNAL="resource.reserve"
    PRE_RELEASE_SIGNAL="resource.prerelease" 
    POST_RELEASE_SIGNAL="resource.postrelease" 

    def __checkResourceType(self, resource):
        if resource and not isinstance(resource,Resource):
            raise UnknownResourceTypeError()

    def __checkDateType(self,date):
        if date and not isinstance(date,datetime):
            raise UnknownDateTimeFormatError()

    def __typeCheckings(self,resource,start=None,end=None,expiration=None):
        #Type checkings
        self.__checkResourceType(resource) 
        self.__checkDateType(startDateTime) 
        self.__checkDateType(endDateTime) 
        self.__checkDateType(expirationDateTime) 
  

#    @abc.abstractmethod
#    def hookPreTemporallyReserve(self, resource, startDateTime, endDateTime, expirationDateTime): 
#        '''
#        Abstract methods to be implemented for the Specific resource Manager
#        '''
#        pass

    #Main Actions over the resevation 
    def temporallyReserve(self, resource, startDateTime, endDateTime, expirationDateTime):
        #Type checkings
        self.__checkTypes(resource, startDateTime, endDateTime, expirationDateTime)
   
        with resource.mutex:
            #XXX 
            resource = ReservationState.temporallyReserve(resource, startDateTime, endDateTime, expirationDateTime)       
                        
        #Notify listeners, MUTEX must be released 
        NotificationCenter.getSignalHandler(self.TEMP__RESERVE_SIGNAL).signal()
        return resource

    def reserve(self, resource, startDateTime, endDateTime, expirationDateTime):
        #Type checkings
        self.__checkTypes(resource, startDateTime, endDateTime, expirationDateTime)
       
        with resource.mutex:
            #XXX 
            resource = ReservationState.reserve(resource, startDateTime, endDateTime, expirationDateTime)       

        #Notify listeners, MUTEX must be released 
        NotificationCenter.getSignalHandler(self.RESERVE_SIGNAL).signal()
        return resource
 
    def updateReservation(self, resource, startDateTime, endDateTime, expirationDateTime):
        #Type checkings
        self.__checkTypes(resource, startDateTime, endDateTime, expirationDateTime)
       
        with resource.mutex:
            #XXX 
            resource = ReservationState.release(resource)      
             
             
        #Notify listeners, MUTEX must be released 
        NotificationCenter.getSignalHandler(self.RESERVE_SIGNAL).signal()
        return resource
    
    def release(self,resource):
        #Type checkings
        self.__checkTypes(resource, startDateTime, endDateTime, expirationDateTime)
       
        #Notify listeners, MUTEX must be released 
        NotificationCenter.getSignalHandler(self.PRE_RELEASE_SIGNAL).signal()
        
        with resource.mutex:
           #XXX 
           ReservationState.release(resource)      
        
        #Notify listeners, MUTEX must be released 
        NotificationCenter.getSignalHandler(self.POST_RELEASE_SIGNAL).signal()
            
        return resource.setReservationState(None)
    
