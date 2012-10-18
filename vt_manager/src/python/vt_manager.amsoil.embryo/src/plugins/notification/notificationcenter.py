from threading import Lock
from blinker import Signal as Bsignal
from ncsignal import Signal

#class Singleton(type):
#    _instances = {}
#    def __call__(cls, *args, **kwargs):
#        if cls not in cls._instances:
#            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#        return cls._instances[cls]
#

class NotificationCenter(object):
    '''
    Interface for the Notification Center
    NotificationCenter only provides signal instances.
    '''
#    #Make NotificationCenter singleton
#    __metaclass__ = Singleton
#
#    _mutex = Lock()
#
#    #Signals container
#    _signals = {}

    @staticmethod
    def getSignal(name = None):
        '''
        Returns a named or unnamed Blinket Signal with unicast/multicast
        properties.
        '''

        if not name:
            return Signal(Bsignal())
        elif isinstance(name,str):
            return Signal(Bsignal(name))
        else:
            raise SignalNameError()

    





