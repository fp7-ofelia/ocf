import abc

from amsoil.core import serviceinterface

from rmr.exception import UndefinedSupportedTypesError, InvalidSupportedResourceTypeError
from rmr.resourcebase import ResourceBase

class ResourceManagerBase(object):
    '''
    Defines basic ResourceManager API 
    '''
    __metaclass__ = abc.ABCMeta

    #Supported Types. **Must** be Resource Types
    @serviceinterface
    def __init__(self, supportedResourceTypes):
        """supportedResourceTypes should be a list of resource types (class definitions which derrive from ResourceBase)."""
        for rtype in supportedResourceTypes:
            if not issubclass(rtype, ResourceBase): 
                raise InvalidSupportedResourceTypeError()
        self._supportedResourceTypes = supportedResourceTypes

    @serviceinterface
    def supportsResourceType(self, theType):
        """
        Returns if this object does support the given resource type.
        The default implementation checks if the given type theType is a subclass in one of the self._supportedResourceTypes.
        Please override if you need to do fancy stuff.
        """
        for sType in self._supportedResourceTypes:
            if issubclass(theType, sType):
                return True
        return False

    # Listing methods
    @serviceinterface
    @abc.abstractmethod
    def list(self, **options):
        '''
        Returns a list of ResourceBase objects

        Implementation MUST signal resource.temporallyreserve signal
        '''
        pass
    
    @serviceinterface
    @abc.abstractmethod
    def find(self, uuid, **options):
        '''
        Returns the resource for the given uuid. Returns None if there is no such resource.

        Implementation MUST signal resource.temporallyreserve signal
        '''
        pass

    # Reservation methods
    @serviceinterface
    @abc.abstractmethod
    def temporallyReserve(self, **options):
        '''
        TODO: explain what is
        
        Implementation MUST signal resource.temporallyreserve signal
        '''
        pass 

    @serviceinterface
    @abc.abstractmethod
    def reserve(self, uuid, **options):
        '''
        reserves the resource.
        If the user has used temporallyReserve before, the {uuid} of this resource should be passed.
        If there was no prior contact, just pass None for {uuid}.
        
        Shall return the resource which has been created.
        
        Implementation MUST signal resource.reserve signal
        '''
        pass

    @serviceinterface
    @abc.abstractmethod
    def release(self, uuid, **options):
        '''
        Terminates the resource

        Implementation MUST signal resource.reserve signal
        '''
        pass

    