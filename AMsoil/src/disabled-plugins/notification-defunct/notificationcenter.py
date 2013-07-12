from threading import Lock
from blinker import Signal as Bsignal
from ncsignal import Signal

class NotificationCenter(object):
    '''
    Interface for the Notification Center
    NotificationCenter only provides signal instances.
    '''

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

    





