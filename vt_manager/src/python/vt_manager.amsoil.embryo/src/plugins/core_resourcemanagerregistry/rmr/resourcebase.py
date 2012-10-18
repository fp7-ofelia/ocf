import abc
import uuid

from amsoil.core import serviceinterface

class ResourceBase(object):
    '''Basic abstract Resource class'''
    __metaclass__ = abc.ABCMeta

    ''' General Attributes''' 
    uuid = None
#    sliceId = None 
#
#    ''' Optional Attributes '''
#    projectId = None 
#    projectName = None
#    sliceName = None 
#    additionalInformation = None 
#    
#    ''' Booking information '''
#    reservationState = None 
#
    '''Operational commands'''
    @serviceinterface
    @abc.abstractmethod
    def start(self):
        pass

    @serviceinterface
    @abc.abstractmethod
    def getOperationalState(self):
        pass 


    @serviceinterface
    def createUUID(self):
        return uuid.uuid4()

#    @abc.abstractmethod
#    def stop():
#        pass 
#
#    '''
#    Resource API 
#    '''
#    #CRUD
#    @abc.abstractmethod
#    @staticmethod
#    def create():
#        pass 
#
#    def update():
#        pass 
#
#    def destroy():
#        pass 
#
#    #Find methods
#    @abc.abstractmethod
#    @staticmethod
#    def find():
#        pass 
#
#    @abc.abstractmethod
#    @staticmethod
#    def findAll():
#        pass 
#

