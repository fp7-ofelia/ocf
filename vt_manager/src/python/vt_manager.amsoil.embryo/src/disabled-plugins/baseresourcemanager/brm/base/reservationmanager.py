from datetime import datetime
from excepts.UnknownDateTimeFormatException import UnknownDateTimeFormatException
from excepts.UnknownReservationStateException import UnknownReservationStateException

'''
    Encapsulates Resource Reservation State machine
 
    State machine cycle
    RELEASED(NULL)      - > TEMP_RESERVED -> RESERVED -> RELEASED(NULL)
                                          \> RELEASED(NULL)

    This class is NOT thread safe
'''

class ReservationState(object):

    #Reservation state-machine states
    TEMP_RESERVED_STATE=0
    RESERVED_STATE=1
    RELEASED_STATE=2
        
    STATES=[TEMP_RESERVED_STATE,RESERVED_STATE,RELEASED_STATE]

    #Reservation information (datetime inst.) 
    start = None
    end = None
    expiration = None

    #State
    state = None

    '''
    Checking utils
    '''
    def __checkDateType(self,date):
        if not isinstance(date,datetime):
            raise UnknownDateTimeFormatException()
    def __checkState(self,state):
        if state not in self.STATES:
            raise UnknownReservationStateException() 

    def __checkTimeFrame(self,start,end,expiration):
        #Check start<end  && end-start <= MAX_RESERVATION_TIME && expiration > now  && expiration-now <= MAX_TEMPORALLY_RESERVE_TIME
   
    '''
    Constructors
    ''' 
    def __init__():
        pass 
    def __init__(self,state,startDateTime=None,endDateTime=None,expirationDateTime=None):
        self.__checkDateType(startDateTime) 
        self.__checkDateType(endDateTime) 
        self.__checkDateType(experationDateTime) 
        
        self.__checkState(state) 
       
        self.state = state
        self.start = startDateTime
        self.end = endDateTime
        self.expiration = expirationDateTime

    '''
    Setters
    '''
    def __setState(self, newState):
        self.__checkState(state) 
        self.state = newState
        return self 

    def __setStart(self, startDateTime):
        self.__checkDateType(startDateTime) 
        self.start = startDateTime
        return self

    def __setEnd(self, endDateTime):
        self.__checkDateType(endDateTime) 
        self.end = endDateTime
        return self
 
    def __setExpiration(self, expirationDateTime):
        self.__checkDateType(expirationDateTime) 
        self.expiration = expirationDateTime
        return self

    '''
    Actions
    '''
    @staticmethod
    def temporallyReserve(resource, start, end, expiration): 
        #Do temporary reservation.
        resource = RSPersistence.get(resource) 

        if ( not resource.reservationState.state == None) and ( not resource.reservationState.state == ReservationState.RELEASED_STATE):
            raise InvalidStateException() 
        ReservationState.__checkTimeFrame(start,end,expiration)
        resource.reservationState.__setState(state).__setStart(start).__setEnd(end).__setExpiration(expiration) 
        return resource

    @staticmethod
    def reserve(resource, start, end, expiration): 
        resource = RSPersistence.get(resource)
          
        if not (resource.reservationState.state == ReservationState.TEMP_RESERVED_STATE):
            raise InvalidStateException() 
        ReservationState.__checkTimeFrame(start,end,expiration)
        resource.reservationState.__setState(state).__setStart(start).__setEnd(end).__setExpiration(expiration) 
        return resource

    @staticmethod
    def updateReservation(resource, start, end, expiration):
        resource = RSPersistence.get(resource) 
        
        if not (resource.reservationState.state == ReservationState.RESERVED_STATE):
            raise InvalidStateException() 
        ReservationState.__checkTimeFrame(start,end,expiration)
        resource.reservationState.__setState(state).__setStart(start).__setEnd(end).__setExpiration(expiration) 
        return resource

    @staticmethod
    def release(resource):
        resource = RSPersistence.get(resource) 
        
        if not (resource.reservationState.state == ReservationState.RESERVED_STATE):
            raise InvalidStateException() 
      
        return RSPersistence.delete(self)  
        
